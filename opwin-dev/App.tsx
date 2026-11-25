import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowRight, ArrowUpRight, ChevronLeft, ChevronRight, Check, MapPin, CalendarDays, MessageSquare, X, Plus, Minus, Bitcoin, ArrowLeft, Info, Send } from "lucide-react";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { consultationSchema, rates, type Consultation, type BookingMode, type Billing } from "@shared/schema";

const todayKey = () => new Intl.DateTimeFormat("en-CA", { timeZone: "America/Los_Angeles", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
const keyFor = (y: number, m: number, d: number) => `${y}-${String(m + 1).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
const prettyDate = (key: string) => new Date(`${key}T12:00:00`).toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric", year: "numeric" });
const faqs = [
  { q: "How does a consultation work?", a: "We talk through the problem, identify what needs attention, and work toward resolving it that day. One client is scheduled per day. The work and scope are discussed with you directly." },
  { q: "Why are the prices different?", a: "Book & pay is $500 per hour or $800 for a flat-rate job. Scheduling directly by text is $200 per hour or $500 for a flat-rate job, after discussing the work. Choose Request a quote if you want to discuss the scope first." },
  { q: "Can I book from outside California?", a: "Online booking is for California only. Out-of-state work must be arranged by text first. Text 252-876-3008 to discuss your consultation." },
  { q: "How do Bitcoin payments work?", a: "Pay with Bitcoin using the address shown at checkout. Your booking is confirmed once payment is received on the blockchain." },
];

export default function App() {
  const today = todayKey();
  const [year, month] = today.split("-").map(Number);
  const [view, setView] = useState(new Date(year, month - 1, 1));
  const [date, setDate] = useState("");
  const [mode, setMode] = useState<BookingMode>("pay");
  const [billing, setBilling] = useState<Billing>("flat");
  const [step, setStep] = useState(0);
  const [details, setDetails] = useState<Consultation | null>(null);
  const [chat, setChat] = useState(false);
  const [serviceArea, setServiceArea] = useState<string | null>(null);
  const [chatItems, setChatItems] = useState<{ role: string; text: string }[]>([]);
  const [question, setQuestion] = useState("");
  const [faq, setFaq] = useState<number | null>(null);
  const [mailReady, setMailReady] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [user, setUser] = useState<{ id: string; email: string; role: string } | null>(null);
  const [authModal, setAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [paymentInvoice, setPaymentInvoice] = useState<{ id: string; amountUsd: number; amountBtc: string; btcAddress: string; status: string } | null>(null);
  const [paymentStatus, setPaymentStatus] = useState<"idle" | "creating" | "success" | "error">("idle");
  const [paymentError, setPaymentError] = useState<string | null>(null);
  const [legalPage, setLegalPage] = useState<"privacy" | "cancellation" | "refund" | null>(null);
  const booking = useRef<HTMLElement>(null);
  const stepTitle = useRef<HTMLHeadingElement>(null);
  const chatInput = useRef<HTMLInputElement>(null);
  const chatLog = useRef<HTMLDivElement>(null);
  const chatButton = useRef<HTMLButtonElement>(null);
  const form = useForm<Consultation>({ resolver: zodResolver(consultationSchema), defaultValues: { name: "", email: "", phone: "", city: "", issue: "", location: "california" } });
  const outOfState = form.watch("location") === "elsewhere";
  const price = rates[mode][billing];
  const dates = Array.from({ length: new Date(view.getFullYear(), view.getMonth() + 1, 0).getDate() }, (_, i) => i + 1);
  const atStart = view.getFullYear() === year && view.getMonth() === month - 1;
  const atEnd = view.getTime() >= new Date(year, month + 6, 1).getTime();

  const emailBody = details ? "Hello Opwin.io,\n\nI would like to discuss a consultation.\nPreferred date (not reserved): " + prettyDate(date) + "\nOption: " + (mode === "pay" ? "Book & pay" : "Direct-scheduling quote") + "\nBilling: " + (billing === "flat" ? "By the job" : "By the hour") + "\nDisplayed rate: " + (details.location === "elsewhere" ? "Requires confirmation for out-of-state work" : "$" + price + "/" + (billing === "flat" ? "job" : "hour")) + "\n\nName: " + details.name + "\nEmail: " + details.email + "\nPhone: " + details.phone + "\nLocation: " + details.city + ", " + (details.location === "california" ? "California" : "outside California") + "\n\n" + details.issue + "\n\nPlease contact me to discuss scope and confirm availability." : "";

  const answer = (q: string) => {
    const lower = q.toLowerCase();
    let a = "I can help with pricing, the consultation process, service area, and payments. For a specific technical question or a quote, contact admin@opwin.io. This FAQ assistant cannot book a date or confirm a payment.";
    if (/price|cost|rate|expensive|cheap|how much/.test(lower)) a = faqs[1].a;
    else if (/bitcoin|crypto|payment|qr/.test(lower)) a = faqs[3].a;
    else if (/outside|state|california|location|where|area/.test(lower)) a = faqs[2].a;
    else if (/work|consult|problem|fix|service/.test(lower)) a = faqs[0].a;
    else if (/text|phone|contact|number/.test(lower)) a = "Text Opwin.io at 252-876-3008, or email admin@opwin.io. Direct scheduling is $200/hour or $500 per job after discussing the scope. Out-of-state consultations must be arranged by text.";
    else if (/book|date|days|week|available|calendar|cancel|refund/.test(lower)) a = "Consultations are offered seven days a week, with only one client scheduled per day. Select a preferred date in the preview calendar to explore the flow. Live availability and payments are not connected yet, and no date is reserved here. Text 252-876-3008 to discuss an appointment or cancellation terms.";
    setChatItems(prev => [...prev, { role: "you", text: q.slice(0, 300) }, { role: "assistant", text: a }]);
    setQuestion("");
  };

  const closeChat = () => { setChat(false); setChatItems([]); setQuestion(""); };
  const backToSuggestions = () => { setChatItems([]); setQuestion(""); };

  const startQuote = () => { setMode("quote"); goto(0); };

  const goto = (next: number) => { setStep(next); setMailReady(false); };

  const submitBooking = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!details) return;
    setSubmitStatus("submitting");
    setSubmitError(null);
    try {
      const payload = {
        date,
        mode,
        billing,
        name: details.name,
        email: details.email,
        phone: details.phone,
        city: details.city,
        location: details.location,
        issue: details.issue,
      };
      const endpoint = mode === "quote" ? "/api/quotes" : "/api/bookings";
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.status === 409) {
        setSubmitStatus("error");
        setSubmitError("This date has already been reserved. Please choose a different day.");
        return;
      }
      if (!res.ok) {
        throw new Error("Submission failed: " + res.status);
      }
      await res.json();
      setSubmitStatus("success");
      if (mode === "pay") {
        goto(3);
        createPaymentInvoice();
      }
    } catch (e: any) {
      setSubmitStatus("error");
      setSubmitError(e.message ?? "Submission failed. Please try again.");
    }
  };

  useEffect(() => { if (step > 0) stepTitle.current?.focus(); }, [step]);
  useEffect(() => { if (chat) chatInput.current?.focus(); }, [chat]);
  useEffect(() => { chatLog.current?.scrollTo({ top: chatLog.current.scrollHeight }); }, [chatItems]);

  useEffect(() => {
    fetch("/api/auth/me")
      .then((r) => r.ok ? r.json() : null)
      .then((data) => data && setUser(data))
      .catch(() => {});
  }, []);

  const login = async (email: string, password: string) => {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error("Invalid email or password");
    const data = await res.json();
    setUser(data);
    setAuthModal(false);
      setProfile(true);
    return data;
  };

  const register = async (email: string, password: string, role: string) => {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, role }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error ?? "Registration failed");
    }
    const data = await res.json();
    setUser(data);
    setAuthModal(false);
    return data;
  };

  const logout = async () => {
    await fetch("/api/auth/logout", { method: "POST" });
    setUser(null);
  };

  const createPaymentInvoice = async () => {
    if (!details) return;
    setPaymentStatus("creating");
    setPaymentError(null);
    try {
      const res = await fetch("/api/payment/invoice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          bookingId: details.email,
          btcAddress: "",
          amountUsd: price,
        }),
      });
      if (!res.ok) throw new Error("Failed to create invoice");
      const invoice = await res.json();
      setPaymentInvoice(invoice);
      setPaymentStatus("success");
    } catch (e: any) {
      setPaymentStatus("error");
      setPaymentError(e.message ?? "Failed to create payment invoice");
    }
  };

        const serviceAreaDescriptions: Record<string, string> = {
        web: "Full stack web development: I build end-to-end web applications — frontend, backend, databases, and deployment. From concept to production, I handle the full stack.",
        cyber: "Cyber security: I secure networks, harden systems, and protect data against threats. Risk assessment, penetration testing, and incident response.",
        av: "Audio video solutions: I install and configure surveillance camera systems, audio setups, and video streaming infrastructure. Getting your gear online and working.",
        ai: "Local AI: I deploy and run local AI models — chatbots, assistants, and automation — on your own hardware. Private, offline, and under your control.",
      };

return (
    <div className="site">
      <a className="skip" href="#main" data-testid="link-skip">Skip to content</a>
      <header className="header wrap">
        <a className="wordmark" href="./" data-testid="link-home" aria-label="Opwin.io home">Opwin<span>.io</span></a>
        <nav aria-label="Main navigation">
          <button onClick={startQuote} data-testid="button-contact">Request a quote <ArrowUpRight size={15} /></button>
          <a href="sms:+12528763008" data-testid="link-text-header">Text 252-876-3008 <ArrowUpRight size={15} /></a>
          <div className="service-dropdown" data-testid="service-dropdown">
            <span className="service-label">Service areas</span>
            <div className="dropdown-menu" data-testid="dropdown-menu">
              <div className="dropdown-option" onClick={() => setServiceArea("web")}>Full stack web development</div>
              <div className="dropdown-option" onClick={() => setServiceArea("cyber")}>Cyber security</div>
              <div className="dropdown-option" onClick={() => setServiceArea("av")}>Audio video solutions</div>
              <div className="dropdown-option" onClick={() => setServiceArea("ai")}>Local AI</div>
            </div>
          </div>
        </nav>
        {user ? (
          <>
            <button className="text-link" onClick={logout} data-testid="button-logout">Sign out ({user.email})</button>
            <button className="chat-launcher" ref={chatButton} onClick={() => chat ? closeChat() : setChat(true)} aria-expanded={chat} aria-label={chat ? "Close quick questions" : "Open quick questions"} data-testid="button-chat">{chat ? <X size={19} /> : <MessageSquare size={19} />}<span>Quick questions</span></button>
          </>
        ) : (
          <>
            <button className="text-link" onClick={() => { setAuthModal(true); setAuthMode("login"); }} data-testid="button-login">Sign in</button>
            <button className="chat-launcher" ref={chatButton} onClick={() => chat ? closeChat() : setChat(true)} aria-expanded={chat} aria-label={chat ? "Close quick questions" : "Open quick questions"} data-testid="button-chat">{chat ? <X size={19} /> : <MessageSquare size={19} />}<span>Quick questions</span></button>
          </>
        )}
      </header>
      <main id="main" className="wrap">
        <div className="preview-notice" role="status"><Info size={14} /><span>Private preview. Explore the booking flow; availability and payments are not live.</span></div>
        <div className="main-grid">
          <section className="intro" aria-labelledby="page-title">
            <div className="eyebrow"><span className="status-dot" /> INDEPENDENT TECH CONSULTING</div>
            <h1 id="page-title">Book your<br /> consultation.</h1>
            <p className="intro-copy">A conversation. A clear plan. Hands-on help.<br className="desktop-break" /> Choose a day to work through your tech.</p>
            <div className="service-notes">
              <div><CalendarDays size={19} /><span>One client. One day.<small>Appointments offered seven days a week.</small></span></div>
              <div><MapPin size={19} /><span>California appointments<small>Out of state? Arrange it by text first.</small></span></div>
            </div>
            <section className="direct-note" aria-labelledby="direct-heading">
              <span className="eyebrow">DIRECT-SCHEDULING RATES</span>
              <h2 id="direct-heading">Let’s start with the problem.</h2>
              <p>Schedule by text for <strong>$200/hour</strong> or <strong>$500 per job</strong>, after we discuss the scope. These are separate from the higher online Book &amp; pay rates.</p>
              <button className="text-link" onClick={startQuote} data-testid="button-intro-quote">Request a quote <ArrowUpRight size={17} /></button>
              <a className="text-link" href="sms:+12528763008" data-testid="link-text-intro">Text 252-876-3008 <ArrowUpRight size={17} /></a>
            </section>
            <div className="intro-foot"><span>YOUR TECH. YOUR DAY.</span><span>OPWIN.IO</span></div>
          </section>
                    {serviceArea && (
            <section className="service-area-view" aria-labelledby="service-area-title">
              <div className="wrap">
                <button onClick={() => setServiceArea(null)} className="close-service" aria-label="Close service area" data-testid="button-close-service">✕</button>
                <h2 id="service-area-title">Service area details</h2>
                <p>{serviceAreaDescriptions[serviceArea]}</p>
              </div>
            </section>
          )}
{!serviceArea && (
          <section className="booking-card" ref={booking} aria-labelledby="booking-title">
            <div className="card-top"><span className="eyebrow">SCHEDULE A CONSULTATION</span><span className="step-caption">0{step + 1} / 04</span></div>
            <ol className="steps" aria-label="Booking progress">
              {["Your appointment", "Your details", "Review", "Pay"].map((label, i) => <li key={label} className={step >= i ? "active" : ""} aria-current={step === i ? "step" : undefined}><span>{step > i ? <Check size={12} /> : i + 1}</span>{label}</li>)}
            </ol>
            {step === 0 && (
              <>
                <div className="mode-tabs" aria-label="Booking type">
                  <button aria-pressed={mode === "pay"} className={mode === "pay" ? "selected" : ""} onClick={() => setMode("pay")} data-testid="button-mode-pay">Book & pay</button>
                  <button aria-pressed={mode === "quote"} className={mode === "quote" ? "selected" : ""} onClick={() => setMode("quote")} data-testid="button-mode-quote">Request a quote</button>
                </div>
                <fieldset className="rate-options"><legend className="sr-only">Choose your pricing</legend>
                  {["flat", "hourly"].map(b => <label key={b} className={"rate-option " + (billing === b ? "chosen" : "")}><input type="radio" name="billing" value={b} checked={billing === b} onChange={() => setBilling(b as Billing)} data-testid={"input-billing-" + b} /><span className="radio-dot" /><span className="rate-label">{b === "flat" ? "By the job" : "By the hour"}<strong>${rates[mode as keyof typeof rates][b as Billing]}<small> / {b === "flat" ? "job" : "hour"}</small></strong></span></label>)}
                </fieldset>
                <p className="rate-help">{mode === "pay" ? (billing === "flat" ? "$800 total for flat-rate work. Bitcoin checkout at payment." : "$500 per hour. Hours and the amount due must be agreed before payment.") : "Direct-scheduling rates. Discuss the scope before committing."}</p>
                <div className="calendar-heading"><h2 id="booking-title">Choose a day</h2><span>Pacific time</span></div>
                <div className="month-nav"><h3 aria-live="polite" data-testid="text-month">{view.toLocaleDateString("en-US", { month: "long", year: "numeric" })}</h3><div><button className="icon-button" onClick={() => setView(new Date(view.getFullYear(), view.getMonth() - 1, 1))} disabled={atStart} aria-label="Previous month" data-testid="button-prev-month"><ChevronLeft size={18} /></button><button className="icon-button" onClick={() => setView(new Date(view.getFullYear(), view.getMonth() + 1, 1))} disabled={atEnd} aria-label="Next month" data-testid="button-next-month"><ChevronRight size={18} /></button></div></div>
                <div className="calendar" role="group" aria-label="Preview date selector">
                  {["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"].map(d => <span className="weekday" key={d}>{d}</span>)}
                  {Array.from({ length: view.getDay() }, (_, i) => <span key={"blank-" + i} />)}
                  {dates.map(d => { const key = keyFor(view.getFullYear(), view.getMonth(), d); const past = key <= today; return <button key={key} className={"day " + (date === key ? "picked" : "")} disabled={past} aria-label={prettyDate(key) + (past ? ", not selectable" : ", preview date")} aria-pressed={date === key} onClick={() => setDate(key)}>{d}{!past && <span className="day-dot" />}</button>; })}
                </div>
                <div className="calendar-legend"><span><i />Preview dates</span><span>Live availability not connected</span></div>
                <div className="selected-summary" aria-live="polite"><CalendarDays size={17} /><span>{date ? prettyDate(date) : "Select your preferred date"}</span></div>
                <button className="primary-button" disabled={!date} onClick={() => goto(1)} data-testid="button-continue">Continue to your details <ArrowRight size={18} /></button>
                <p className="under-button">No payment or reservation is made in this preview.</p>
              </>
            )}
            {step === 1 && (
              <>
                <button className="back-link" onClick={() => goto(0)} data-testid="button-back-date"><ArrowLeft size={15} /> Appointment</button>
                <h2 className="step-title" ref={stepTitle} tabIndex={-1} id="booking-title">Tell me what’s going on.</h2>
                <p className="step-desc">A few details to understand the problem before your consultation.</p>
                <div className="compact-summary"><CalendarDays size={16} /><span>{prettyDate(date)}<small>{mode === "pay" ? "Book & pay" : "Request a quote"} · ${price}/{billing === "flat" ? "job" : "hour"}</small></span><button onClick={() => goto(0)} data-testid="button-edit-appointment">Edit</button></div>
                <Form {...form}><form onSubmit={form.handleSubmit(values => { setDetails(values); goto(2); })} noValidate>
                  <div className="form-grid">
                    {["name", "email", "phone", "city"].map((name) => <FormField key={name as "name" | "email" | "phone" | "city"} control={form.control} name={name as "name" | "email" | "phone" | "city"} render={({ field }) => <FormItem><FormLabel>{({ name: "Your name", email: "Email address", phone: "Phone number", city: "City" })[name]}</FormLabel><FormControl><input {...field} type={name === "email" ? "email" : name === "phone" ? "tel" : "text"} autoComplete={({ name: "name", email: "email", phone: "tel", city: "address-level2" })[name]} placeholder={({ name: "Full name", email: "you@example.com", phone: "(555) 000-0000", city: "Your city" })[name]} data-testid={"input-" + name} /></FormControl><FormMessage /></FormItem>} />)}
                  </div>
                  <FormField control={form.control} name="location" render={({ field }) => <FormItem className="form-block"><FormLabel>Where do you need help?</FormLabel><FormControl><select {...field} data-testid="select-location"><option value="california">California</option><option value="elsewhere">Outside California</option></select></FormControl><FormMessage /></FormItem>} />
                  {outOfState && <div className="inline-notice" role="status">Out-of-state consultations must be arranged by text first. You can review your inquiry here, but you cannot book or pay online.</div>}
                  <FormField control={form.control} name="issue" render={({ field }) => <FormItem className="form-block"><FormLabel>What would you like help with?</FormLabel><FormControl><textarea {...field} rows={4} maxLength={1500} placeholder="Describe the issue, the devices involved, and what you’d like to achieve." data-testid="input-issue" /></FormControl><FormMessage /></FormItem>} />
                  <p className="privacy-note">Please don’t include passwords or sensitive files. Your details are submitted to Opwin.io’s backend to be reviewed and stored, per the project’s privacy policy.</p>
                  <button type="submit" className="primary-button" data-testid="button-review">{outOfState || mode === "quote" ? "Review your inquiry" : "Review your appointment"}<ArrowRight size={18} /></button>
                </form></Form>
              </>
            )}
            {step === 2 && details && (
              <>
                <button className="back-link" onClick={() => goto(1)} data-testid="button-back-details"><ArrowLeft size={15} /> Your details</button>
                <h2 className="step-title" ref={stepTitle} tabIndex={-1} id="booking-title">{details.location === "elsewhere" || mode === "quote" ? "Let’s review your inquiry." : "Your consultation, at a glance."}</h2>
                <p className="step-desc">Review the details before submitting.</p>
                <dl className="review-list">
                  <div><dt>Preferred day</dt><dd>{prettyDate(date)}<small>Subject to live availability</small></dd></div>
                  <div><dt>Consultation</dt><dd>{mode === "pay" ? "Book & pay" : "Direct-scheduling quote"}<small>{billing === "flat" ? "Flat-rate job" : "Hourly consultation"}</small></dd></div>
                  <div><dt>Contact</dt><dd>{details.name}<small>{details.email}<br />{details.phone}</small></dd></div>
                  <div><dt>Location</dt><dd>{details.city}<small>{details.location === "california" ? "California" : "Outside California · arrange by text"}</small></dd></div>
                  <div><dt>The problem</dt><dd>{details.issue}</dd></div>
                </dl>
                <div className="total"><span>{details.location === "elsewhere" ? "Rate requires confirmation" : billing === "flat" ? "Flat-rate total" : "Hourly rate"}<small>USD · {mode === "quote" ? "Subject to scope discussion" : billing === "hourly" ? "Hours to be agreed before payment" : "By-the-job consultation"}</small></span><strong>{details.location === "elsewhere" ? "TBD" : "$" + price}{billing === "hourly" && details.location !== "elsewhere" && <small>/hr</small>}</strong></div>
                <div className="activation-notice"><Bitcoin size={22} /><div><strong>{details.location === "elsewhere" ? "Arrange out-of-state work directly" : mode === "pay" ? "Bitcoin checkout is not connected yet" : "Online quote requests are not connected yet"}</strong><p>{details.location === "elsewhere" ? "Text 252-876-3008 to arrange your consultation. Online dates and rates do not confirm an out-of-state appointment." : "This is a private preview. No date is held and no payment is due. You can text or email an inquiry instead; the date must be confirmed directly."}</p></div></div>
                <button className="primary-button" onClick={submitBooking} disabled={submitStatus !== "idle"} data-testid="button-submit-booking">{details.location === "elsewhere" || mode === "quote" ? "Submit inquiry" : "Book appointment"}<ArrowRight size={18} /></button>
                {details.location === "elsewhere" || mode === "quote" && <p className="under-button">Out-of-state and quote requests will be reviewed before any date is confirmed.</p>}
                <a className="text-link" href="sms:+12528763008" data-testid="link-text-review">Text 252-876-3008 <ArrowUpRight size={17} /></a>
                <a className="text-link" href={"mailto:admin@opwin.io?subject=" + encodeURIComponent("Consultation inquiry - " + date) + "&body=" + encodeURIComponent(emailBody)} data-testid="link-email-inquiry">Open email instead <ArrowUpRight size={18} /></a>
                <p className="under-button">No Bitcoin address or QR code is displayed until payment setup is verified.</p>
              </>
            )}
            {step === 3 && (
              <>
                <button className="back-link" onClick={() => goto(2)} data-testid="button-back-review"><ArrowLeft size={15} /> Review</button>
                <h2 className="step-title" ref={stepTitle} tabIndex={-1} id="booking-title">Bitcoin payment</h2>
                <p className="step-desc">Scan the QR code or copy the address to pay.</p>
                <div className="payment-card">
                  <div className="qr-code">
                    <svg width="200" height="200" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect width="200" height="200" fill="white"/>
                      <text x="100" y="100" font-family="Arial" font-size="14" fill="#666" text-anchor="middle">QR Code</text>
                    </svg>
                    {paymentInvoice && <p className="btc-uri">bitcoin:{paymentInvoice.btcAddress}?amount={paymentInvoice.amountBtc}</p>}
                  </div>
                  <div className="payment-details">
                    <div><span>Amount</span><strong>${paymentInvoice?.amountUsd}</strong></div>
                    <div><span>Bitcoin (≈)</span><strong>{paymentInvoice?.amountBtc} BTC</strong></div>
                    <div><span>Address</span><code>{paymentInvoice?.btcAddress}</code></div>
                    <div><span>Status</span><strong>{paymentInvoice?.status}</strong></div>
                  </div>
                  <button className="primary-button" onClick={() => { setPaymentStatus("idle"); goto(0); }} data-testid="button-payment-done">Done<ArrowRight size={18} /></button>
                  <p className="under-button">Payment is manually verified. You will receive email confirmation once confirmed.</p>
                </div>
              </>
            )}
          </section>
          )}
        </div>
        <section className="faq-section" aria-labelledby="faq-title">
          <div><span className="eyebrow">BEFORE YOU BOOK</span><h2 id="faq-title">A few useful details.</h2><p>Something else on your mind?<br /><a href="sms:+12528763008" data-testid="link-text-faq">Text 252-876-3008 <ArrowUpRight size={14} /></a><br /><a href="mailto:admin@opwin.io" data-testid="link-faq-email">admin@opwin.io <ArrowUpRight size={14} /></a></p></div>
          <div className="faq-list">{faqs.map((item, i) => <article key={item.q}><h3><button aria-expanded={faq === i} aria-controls={"faq-" + i} onClick={() => setFaq(faq === i ? null : i)} data-testid={"button-faq-" + i}>{item.q}{faq === i ? <Minus size={17} /> : <Plus size={17} />}</button></h3><div id={"faq-" + i} hidden={faq !== i}><p>{item.a}</p></div></article>)}</div>
        </section>
      </main>
      <footer className="footer wrap"><span className="footer-brand">Opwin.io</span><span>Independent tech consulting · California</span><a href="mailto:admin@opwin.io" data-testid="link-footer-email">admin@opwin.io <ArrowUpRight size={14} /></a><div className="footer-links"><button onClick={() => setLegalPage("privacy")} data-testid="link-privacy">Privacy</button><button onClick={() => setLegalPage("cancellation")} data-testid="link-cancellation">Cancellation</button><button onClick={() => setLegalPage("refund")} data-testid="link-refund">Refund</button></div></footer>
      {chat && (
        <aside className="chat-panel" aria-label="Opwin.io FAQ assistant" onKeyDown={e => { if (e.key === "Escape") closeChat(); }}>
          <div className="chat-header">
            <div>
              <strong>Ask Opwin.io</strong>
              <small>Quick answers · FAQ assistant</small>
            </div>
            {chatItems.length > 0 && (
              <button className="icon-button" onClick={backToSuggestions} aria-label="Back to suggestions" data-testid="button-back-to-suggestions"><ArrowLeft size={17} /></button>
            )}
            <button className="icon-button" onClick={closeChat} aria-label="Close FAQ assistant" data-testid="button-close-chat"><X size={19} /></button>
          </div>
          <div className="chat-log" ref={chatLog} role="log" aria-live="polite">
            {chatItems.length === 0 && (
              <div className="bubble assistant">Hi. I can help with pricing, service area, and how consultations work. What would you like to know?</div>
            )}
            {chatItems.map((item, i) => (
              <div key={i} className={"bubble " + item.role}>{item.text}</div>
            ))}
            {chatItems.length === 0 && (
              <div className="chat-suggestions">
                {["What does it cost?", "How does a consultation work?", "Outside California?", "Bitcoin payments?"].map((q) => (
                  <button key={q} onClick={() => answer(q)} data-testid={"chat-suggestion-" + q.split(" ")[0]}>
                    {q}
                    <ArrowUpRight size={13} />
                  </button>
                ))}
              </div>
            )}
          </div>
          <form className="chat-form" onSubmit={e => { e.preventDefault(); answer(question); }}>
            <label className="sr-only" htmlFor="chat-question">Ask a question</label>
            <input id="chat-question" ref={chatInput} value={question} onChange={e => setQuestion(e.target.value)} maxLength={300} placeholder="Ask a quick question…" data-testid="input-chat" />
            <button type="submit" aria-label="Send question" disabled={!question.trim()} data-testid="button-send-chat"><Send size={17} /></button>
          </form>
          <p className="chat-disclaimer">Automated FAQ, not a live chat. No messages are sent.</p>
        </aside>
      )}
      {profile && (
        <div className="auth-modal-overlay" onClick={() => setProfile(false)}>
          <div className="auth-modal" onClick={e => e.stopPropagation()}>
            <button className="auth-close" onClick={() => setProfile(false)}>×</button>
            <h2>Your Profile</h2>
            <div className="profile-content">
              <p className="profile-anon">Keeping you anonymous.</p>
              <h3>Free Cybersecurity Tools</h3>
              <div className="tool-grid">
                <div className="tool-card">
                  <h4>DNS Leak Test</h4>
                  <p>Check if your DNS requests are leaking outside your VPN.</p>
                  <button className="primary-button" disabled>Run Test</button>
                </div>
                <div className="tool-card">
                  <h4>What's My IP?</h4>
                  <p>See your public IP address and location.</p>
                  <button className="primary-button" disabled>Check IP</button>
                </div>
                <div className="tool-card">
                  <h4>Background Check Removal</h4>
                  <p>Request removal of your info from background check websites.</p>
                  <button className="primary-button" disabled>Start Removal</button>
                </div>
              </div>
              <p className="profile-note">More tools coming soon. All tools are free and run through secure APIs.</p>
            </div>
            <button className="primary-button" onClick={() => setProfile(false)}>Close</button>
          </div>
        </div>
      )}
      {authModal && (
        <div className="auth-modal-overlay" onClick={() => setAuthModal(false)}>
          <div className="auth-modal" onClick={e => e.stopPropagation()}>
            <button className="auth-close" onClick={() => setAuthModal(false)}>×</button>
            <h2>{authMode === "login" ? "Sign in" : "Create account"}</h2>
            <form onSubmit={async (e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const email = formData.get("email") as string;
              const password = formData.get("password") as string;
              try {
                if (authMode === "login") {
                  await login(email, password);
                } else {
                  const role = (formData.get("role") as string) || "customer";
                  await register(email, password, role);
                }
              } catch (err: any) {
                alert(err.message);
              }
            }}>
              <div className="auth-field"><label>Email</label><input type="email" name="email" required /></div>
              <div className="auth-field"><label>Password</label><input type="password" name="password" required /></div>
              {authMode === "register" && (
                <div className="auth-field"><label>Role</label><select name="role"><option value="customer">Customer</option></select></div>
              )}
              <button type="submit" className="primary-button">{authMode === "login" ? "Sign in" : "Create account"}</button>
              <p className="auth-toggle">{authMode === "login" ? "Don't have an account? " : "Already have an account? "}<button type="button" onClick={() => setAuthMode(authMode === "login" ? "register" : "login")} className="text-link">{authMode === "login" ? "Create one" : "Sign in"}</button></p>
            </form>
          </div>
        </div>
      )}
      {legalPage && (
        <div className="legal-modal-overlay" onClick={() => setLegalPage(null)}>
          <div className="legal-modal" onClick={e => e.stopPropagation()}>
            <button className="auth-close" onClick={() => setLegalPage(null)}>×</button>
            <h2>{legalPage === "privacy" ? "Privacy" : legalPage === "cancellation" ? "Cancellation" : "Refund"}</h2>
            <div className="legal-content">
              {legalPage === "privacy" && (
                <>
                  <p>Opwin.io collects your name, email, phone, city, and consultation details solely to schedule and confirm your appointment.</p>
                  <p>We do not sell your data. Payment is handled in Bitcoin; we do not store wallet private keys.</p>
                  <p>Contact: admin@opwin.io</p>
                </>
              )}
              {legalPage === "cancellation" && (
                <>
                  <p>You may cancel your consultation up to 24 hours before your scheduled date.</p>
                  <p>Bitcoin payments are final once confirmed on the blockchain. Refunds, if any, are issued at our discretion.</p>
                  <p>Contact: admin@opwin.io or text 252-876-3008.</p>
                </>
              )}
              {legalPage === "refund" && (
                <>
                  <p>Refunds are considered on a case-by-case basis for cancelled consultations.</p>
                  <p>Bitcoin refunds are sent to the original payment address.</p>
                  <p>Contact: admin@opwin.io</p>
                </>
              )}
            </div>
            <button className="primary-button" onClick={() => setLegalPage(null)}>Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
