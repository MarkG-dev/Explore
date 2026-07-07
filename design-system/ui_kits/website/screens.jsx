/* Loop X — Website UI kit screens.
   Composes design-system components from window.LoopXDesignSystem_d0e166.
   Recreation of the marketing site: dark hero, product grid, footer. */
const { Logo, Navbar, Button, ProductCard, Eyebrow } = window.LoopXDesignSystem_d0e166;
const IMG = "../../assets/img";

/* ---- Hero (Home) ---------------------------------------------------- */
function Hero({ nav }) {
  return (
    <section style={{ position: "relative", height: "100%", background: "var(--lx-black)", color: "var(--lx-off-white)", overflow: "hidden" }}>
      <img src={`${IMG}/thermal-vehicle.png`} alt=""
        style={{ position: "absolute", inset: 0, width: "100%", height: "78%", objectFit: "cover", opacity: 0.85, filter: "grayscale(1) contrast(1.08)" }} />
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,.65) 72%, #000 100%)" }} />

      <div style={{ position: "relative", padding: "36px 56px 0" }}>{nav}</div>

      <div style={{ position: "relative", padding: "0 56px", marginTop: 64, maxWidth: 720 }}>
        <h1 className="lx-h1" style={{ margin: 0, fontSize: 68, lineHeight: 0.92 }}>All condition<br/>intelligence</h1>
        <p style={{ fontFamily: "var(--font-primary)", fontSize: 16, lineHeight: 1.35, maxWidth: 380, opacity: 0.85, marginTop: 20 }}>
          Thermal perception that works in any condition — no tag, no map, and no light required.
        </p>
        <div style={{ marginTop: 24 }}>
          <Button tone="light" arrow>More info</Button>
        </div>
      </div>

      <div style={{ position: "absolute", left: 40, right: 40, bottom: 24 }}>
        <Logo height={132} tone="var(--lx-off-white)" style={{ width: "100%", height: "auto" }} />
      </div>
    </section>
  );
}

/* ---- Products (Solutions) ------------------------------------------- */
const PRODUCTS = [
  { title: "Collision Avoidance System", description: "The industry's first safety solution for underground and surface mining, fusing Vision AI, LiDAR and RF into one platform — 360° detection, proactive warnings and automatic intervention." },
  { title: "Load Sight System", description: "Volumetric load intelligence for haul cycles. See payload, spillage and fill in real time, in dust and total dark." },
  { title: "LoopX SLAM", description: "LiDAR, GPS, satellite imagery and inertial sensors fused for precise vehicle localization and mapping where GPS fails." },
];

function Products({ nav }) {
  return (
    <section style={{ height: "100%", background: "var(--lx-off-white)", color: "var(--lx-black)", overflow: "auto" }}>
      <div style={{ padding: "36px 56px 0" }}>{nav}</div>
      <div style={{ padding: "48px 56px 56px" }}>
        <Eyebrow>Platform</Eyebrow>
        <h2 className="lx-h1" style={{ margin: "16px 0 40px", fontSize: 52 }}>Machine intelligence for<br/>uncontrolled environments</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20 }}>
          {PRODUCTS.map((p) => <ProductCard key={p.title} {...p} />)}
        </div>
      </div>
    </section>
  );
}

/* ---- About ---------------------------------------------------------- */
function About({ nav }) {
  return (
    <section style={{ height: "100%", background: "var(--lx-black)", color: "var(--lx-off-white)", overflow: "auto" }}>
      <div style={{ padding: "36px 56px 0" }}>{nav}</div>
      <div style={{ padding: "56px 56px", display: "grid", gridTemplateColumns: "1fr 1.3fr", gap: 56, alignItems: "start" }}>
        <div>
          <Eyebrow tone="light">Shared belief</Eyebrow>
          <h2 className="lx-h2" style={{ margin: "16px 0 0", fontSize: 34 }}>The most dangerous environments deserve the most intelligence</h2>
        </div>
        <div style={{ fontFamily: "var(--font-primary)", fontSize: 18, lineHeight: 1.5, opacity: 0.9 }}>
          <p style={{ marginTop: 0 }}>The most advanced machine vision has always been built for the easy places — the warehouse, the highway, the sunlit road — leaving the people in the hardest, most dangerous conditions in the blind spot.</p>
          <p>So we started where it's hardest, on the principle that autonomy is won in the dark. Build perception there, and the ladder builds itself.</p>
          <div style={{ marginTop: 24 }}><Button tone="light" variant="ghost" arrow>Our strategy</Button></div>
        </div>
      </div>
      <div style={{ padding: "0 56px 48px" }}>
        <img src={`${IMG}/thermal-terrain.png`} alt="" className="lx-chamfer"
          style={{ "--chamfer": "16px", width: "100%", height: 300, objectFit: "cover", filter: "grayscale(1) contrast(1.05)" }} />
      </div>
    </section>
  );
}

window.LoopXSite = { Hero, Products, About };
