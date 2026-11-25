import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# These tests exercise the agent logic without requiring a running model or network.
sys.modules.setdefault('openai', types.SimpleNamespace(OpenAI=object))
sys.modules.setdefault('requests', types.ModuleType('requests'))
sys.modules.setdefault('yaml', types.ModuleType('yaml'))
from agent import config, loop
from agent.tools import TOOLS, dispatch


def response(content=None, calls=None):
    return types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content=content, tool_calls=calls))])


def call(name, args, id):
    return types.SimpleNamespace(id=id, function=types.SimpleNamespace(name=name, arguments=args))


class AgentTests(unittest.TestCase):
    def test_required_fields_inside_schema(self):
        for tool in TOOLS:
            fn = tool['function']
            self.assertNotIn('required', fn)
            for field in fn['parameters'].get('required', []):
                self.assertIn(field, fn['parameters']['properties'])
        self.assertEqual(TOOLS[0]['function']['parameters']['required'], ['query'])

    def test_shell_always_requires_approval_even_for_chains(self):
        with patch.dict(config.CFG, {'allow_shell': True, 'auto_approve_shell': True}, clear=True), patch('builtins.input', return_value='n'), patch('agent.tools.shell') as run:
            result = dispatch('shell', {'command': 'Write-Output x; dangerous-command'})
            self.assertIn('refused', result['content'])
            run.assert_not_called()

    def test_conversation_retains_answer(self):
        client = types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **kw: response('hello'))))
        messages = [{'role': 'user', 'content': 'hi'}]
        self.assertEqual(loop.run_turn(client, 'model', messages), 'hello')
        self.assertEqual(messages[-1], {'role': 'assistant', 'content': 'hello'})

    def test_multiple_tool_results_precede_image_and_failure_is_reported(self):
        calls = [call('screenshot', '{}', '1'), call('bad', '{}', '2')]
        replies = iter([response(calls=calls), response('done')])
        client = types.SimpleNamespace(chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=lambda **kw: next(replies))))
        def execute(name, args):
            if name == 'bad':
                raise RuntimeError('failure')
            return {'content': 'screen', 'image_b64': 'abc'}
        messages = [{'role': 'user', 'content': 'hi'}]
        with patch('agent.loop.dispatch', side_effect=execute):
            self.assertEqual(loop.run_turn(client, 'model', messages), 'done')
        self.assertEqual([m.get('role') if isinstance(m, dict) else 'assistant' for m in messages], ['system', 'user', 'assistant', 'tool', 'tool', 'user', 'assistant'])
        self.assertIn('failure', messages[4]['content'])

    def test_shell_handles_non_utf8_output(self):
        from agent.tools.shell import shell
        with patch('agent.tools.shell.platform.system', return_value='Linux'):
            output = shell("printf '\\203'")
        self.assertEqual(output, '\ufffd')

    def test_windows_shell_requests_utf8(self):
        from agent.tools.shell import shell
        completed = types.SimpleNamespace(stdout='é', stderr='', returncode=0)
        with patch('agent.tools.shell.platform.system', return_value='Windows'), patch('agent.tools.shell.subprocess.run', return_value=completed) as run:
            self.assertEqual(shell('Get-Content file'), 'é')
        self.assertIn('[Console]::OutputEncoding', run.call_args.args[0][-1])
        self.assertEqual(run.call_args.kwargs['encoding'], 'utf-8')
        self.assertEqual(run.call_args.kwargs['errors'], 'replace')

    def test_default_config_path(self):
        self.assertEqual(Path(config.CFG_PATH), Path(__file__).resolve().parents[1] / 'config.yaml')


if __name__ == '__main__':
    unittest.main()
