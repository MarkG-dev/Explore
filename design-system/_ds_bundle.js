/* @ds-bundle: {"format":4,"namespace":"LoopXDesignSystem_d0e166","components":[{"name":"Logo","sourcePath":"components/brand/Logo.jsx"},{"name":"Eyebrow","sourcePath":"components/content/Eyebrow.jsx"},{"name":"ProductCard","sourcePath":"components/content/ProductCard.jsx"},{"name":"Button","sourcePath":"components/controls/Button.jsx"},{"name":"PageHeader","sourcePath":"components/layout/PageHeader.jsx"},{"name":"Panel","sourcePath":"components/layout/Panel.jsx"},{"name":"Navbar","sourcePath":"components/navigation/Navbar.jsx"}],"sourceHashes":{"components/brand/Logo.jsx":"d922d3248091","components/content/Eyebrow.jsx":"4f419dcc6c1f","components/content/ProductCard.jsx":"93263c877c78","components/controls/Button.jsx":"47c84dd96ef6","components/layout/PageHeader.jsx":"368eee43cca6","components/layout/Panel.jsx":"0858b95f0725","components/navigation/Navbar.jsx":"b1c411f0b587","ui_kits/website/screens.jsx":"b20d8a8efe53"},"inlinedExternals":[],"unexposedExports":[]} */

(() => {

const __ds_ns = (window.LoopXDesignSystem_d0e166 = window.LoopXDesignSystem_d0e166 || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// components/brand/Logo.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Loop X logo — the official wordmark and the standalone symbol (X).
 * Vector artwork transcribed verbatim from the brand file. Paints in
 * `currentColor`, so set `color` (or the `tone` prop) on/around it.
 * Never redraw, recolour internally, stretch, or decorate the mark.
 */
const WORDMARK = [
// L
{
  x: 0,
  w: 307.285,
  d: "M 53.486 178.813 L 53.486 0 L 0 0 L 0 199.263 L 46.67 245.933 L 307.285 245.933 L 307.285 192.446 L 67.645 192.446 L 53.486 178.813 Z"
},
// O
{
  x: 339.797,
  w: 323.541,
  d: "M 46.67 0 L 0 46.67 L 0 199.263 L 46.67 245.933 L 276.871 245.933 L 323.541 199.263 L 323.541 46.67 L 276.871 0 L 46.67 0 Z M 270.054 177.764 L 255.372 192.446 L 68.693 192.446 L 53.486 177.239 L 53.486 68.693 L 68.169 53.486 L 254.847 53.486 L 270.054 68.169 L 270.054 177.239 L 270.054 177.764 Z"
},
// O
{
  x: 701.09,
  w: 323.541,
  d: "M 46.67 0 L 0 46.67 L 0 199.263 L 46.67 245.933 L 276.871 245.933 L 323.541 199.263 L 323.541 46.67 L 276.871 0 L 46.67 0 Z M 270.054 177.764 L 255.372 192.446 L 68.693 192.446 L 53.486 177.239 L 53.486 68.693 L 68.169 53.486 L 254.847 53.486 L 270.054 68.169 L 270.054 177.239 L 270.054 177.764 Z"
},
// P
{
  x: 1062.392,
  w: 323.541,
  d: "M 46.67 0 L 0 46.67 L 0 245.933 L 53.486 245.933 L 53.486 181.959 L 276.871 181.959 L 323.541 135.289 L 323.541 46.67 L 276.871 0 L 46.67 0 Z M 270.054 114.314 L 255.896 128.997 L 54.011 128.997 L 54.011 68.693 L 68.693 54.011 L 255.896 54.011 L 270.579 68.693 L 270.579 114.839 L 270.054 114.314 Z"
},
// X
{
  x: 1498.136,
  w: 323.541,
  d: "M 0 246.457 L 15.207 246.457 L 111.168 149.972 L 211.848 149.972 L 307.809 246.457 L 323.541 246.457 L 323.541 184.056 L 262.189 122.704 L 323.541 61.352 L 323.541 0 L 306.761 0 L 211.848 94.912 L 111.168 94.912 L 16.256 0 L 0 0 L 0 61.352 L 60.828 122.704 L 0 184.056 L 0 246.457 Z"
}];
const SYMBOL_PATH = "M 0 383.831 L 23.683 383.831 L 173.132 233.565 L 329.931 233.565 L 479.38 383.831 L 503.88 383.831 L 503.88 286.648 L 408.331 191.099 L 503.88 95.549 L 503.88 0 L 477.747 0 L 329.931 147.816 L 173.132 147.816 L 25.316 0 L 0 0 L 0 95.549 L 94.733 191.099 L 0 286.648 L 0 383.831 Z";
function Logo({
  variant = "wordmark",
  height = 40,
  tone,
  title = "Loop X",
  className,
  style,
  ...rest
}) {
  const colorStyle = tone ? {
    color: tone
  } : null;
  if (variant === "symbol") {
    const w = height * (503.88 / 383.831);
    return /*#__PURE__*/React.createElement("svg", _extends({
      role: "img",
      "aria-label": title,
      viewBox: "0 0 503.88 383.831",
      width: w,
      height: height,
      className: className,
      style: {
        display: "block",
        ...colorStyle,
        ...style
      }
    }, rest), /*#__PURE__*/React.createElement("title", null, title), /*#__PURE__*/React.createElement("path", {
      d: SYMBOL_PATH,
      fill: "currentColor",
      fillRule: "nonzero"
    }));
  }
  const VB_W = 1821.677;
  const VB_H = 246.457;
  const w = height * (VB_W / VB_H);
  return /*#__PURE__*/React.createElement("svg", _extends({
    role: "img",
    "aria-label": title,
    viewBox: `0 0 ${VB_W} ${VB_H}`,
    width: w,
    height: height,
    className: className,
    style: {
      display: "block",
      ...colorStyle,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("title", null, title), WORDMARK.map((g, i) => /*#__PURE__*/React.createElement("path", {
    key: i,
    transform: `translate(${g.x} 0)`,
    d: g.d,
    fill: "currentColor",
    fillRule: "nonzero"
  })));
}
Object.assign(__ds_scope, { Logo });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/brand/Logo.jsx", error: String((e && e.message) || e) }); }

// components/content/Eyebrow.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Loop X eyebrow / label — DM Mono, uppercase, small. Optionally
 * wrapped in the signature chamfered hairline frame ("EYEBROW TEXT").
 * Used above headlines and to tag sections.
 */
function Eyebrow({
  children,
  framed = false,
  tone = "dark",
  // "dark" ink on light | "light" ink on dark
  className,
  style,
  ...rest
}) {
  const ink = tone === "light" ? "var(--lx-off-white)" : "var(--lx-black)";
  const label = {
    fontFamily: "var(--font-mono)",
    fontWeight: 400,
    fontSize: 12,
    lineHeight: 1.25,
    letterSpacing: "0.06em",
    textTransform: "uppercase",
    color: ink
  };
  if (!framed) {
    return /*#__PURE__*/React.createElement("span", _extends({
      className: className,
      style: {
        ...label,
        ...style
      }
    }, rest), children);
  }
  return /*#__PURE__*/React.createElement("span", _extends({
    className: `lx-chamfer ${className || ""}`,
    style: {
      ...label,
      display: "inline-flex",
      alignItems: "center",
      padding: "6px 12px",
      border: `1px solid ${ink}`,
      ["--chamfer"]: "5px",
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Eyebrow });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/Eyebrow.jsx", error: String((e && e.message) || e) }); }

// components/controls/Button.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Loop X button — the signature chamfered ("cut corner") control.
 * DM Mono, uppercase. Outline by default; solid for primary emphasis.
 * The chamfer echoes the notched LOOP X letterforms.
 */
function Button({
  children,
  variant = "outline",
  // "outline" | "solid" | "ghost"
  tone = "dark",
  // "dark" (on light bg) | "light" (on dark bg)
  size = "md",
  // "sm" | "md" | "lg"
  arrow = false,
  as = "button",
  className,
  style,
  ...rest
}) {
  const Tag = as;
  const onDark = tone === "light";
  const ink = onDark ? "var(--lx-off-white)" : "var(--lx-black)";
  const paper = onDark ? "var(--lx-black)" : "var(--lx-off-white)";
  const pad = {
    sm: {
      padding: "7px 14px",
      fontSize: 11,
      chamfer: 5
    },
    md: {
      padding: "11px 20px",
      fontSize: 12,
      chamfer: 7
    },
    lg: {
      padding: "15px 28px",
      fontSize: 14,
      chamfer: 9
    }
  }[size];
  const solid = variant === "solid";
  const ghost = variant === "ghost";
  const base = {
    display: "inline-flex",
    alignItems: "center",
    gap: 10,
    padding: pad.padding,
    fontFamily: "var(--font-mono)",
    fontWeight: 400,
    fontSize: pad.fontSize,
    lineHeight: 1,
    letterSpacing: "0.04em",
    textTransform: "uppercase",
    color: solid ? paper : ink,
    background: solid ? ink : "transparent",
    border: ghost ? "none" : `var(--border-med) solid ${ink}`,
    cursor: "pointer",
    whiteSpace: "nowrap",
    transition: "opacity var(--dur-fast) var(--ease-standard), background var(--dur-fast) var(--ease-standard)",
    ["--chamfer"]: `${pad.chamfer}px`,
    ...style
  };
  return /*#__PURE__*/React.createElement(Tag, _extends({
    className: `lx-chamfer ${className || ""}`,
    style: base,
    onMouseEnter: e => e.currentTarget.style.opacity = "0.62",
    onMouseLeave: e => e.currentTarget.style.opacity = "1"
  }, rest), children, arrow && /*#__PURE__*/React.createElement("svg", {
    width: "13",
    height: "10",
    viewBox: "0 0 13 10",
    fill: "none",
    "aria-hidden": "true",
    style: {
      flexShrink: 0
    }
  }, /*#__PURE__*/React.createElement("path", {
    d: "M8 1L12 5L8 9",
    stroke: "currentColor",
    strokeWidth: "1.3"
  }), /*#__PURE__*/React.createElement("path", {
    d: "M0 5H12",
    stroke: "currentColor",
    strokeWidth: "1.3"
  })));
}
Object.assign(__ds_scope, { Button });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/controls/Button.jsx", error: String((e && e.message) || e) }); }

// components/content/ProductCard.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Loop X product card — a chamfered, hairline-framed block pairing a
 * title, short description and a "more info" action. Matches the
 * product tiles used on the site and in decks.
 */
function ProductCard({
  title,
  description,
  action = "MORE INFO",
  tone = "light",
  // "light" | "dark"
  onAction,
  className,
  style,
  ...rest
}) {
  const onDark = tone === "dark";
  const ink = onDark ? "var(--lx-off-white)" : "var(--lx-black)";
  return /*#__PURE__*/React.createElement("div", _extends({
    className: `lx-chamfer ${className || ""}`,
    style: {
      ["--chamfer"]: "12px",
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
      gap: 24,
      padding: 28,
      minHeight: 260,
      border: `1px solid ${ink}`,
      background: onDark ? "var(--lx-black)" : "transparent",
      color: ink,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("h3", {
    style: {
      margin: 0,
      fontFamily: "var(--font-primary)",
      fontWeight: 400,
      fontSize: 30,
      lineHeight: 0.9,
      textTransform: "uppercase"
    }
  }, title), /*#__PURE__*/React.createElement("p", {
    style: {
      margin: 0,
      fontFamily: "var(--font-primary)",
      fontWeight: 400,
      fontSize: 14,
      lineHeight: 1.35,
      opacity: 0.82,
      flex: "0 1 auto"
    }
  }, description), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(__ds_scope.Button, {
    size: "sm",
    tone: onDark ? "light" : "dark",
    arrow: true,
    onClick: onAction
  }, action)));
}
Object.assign(__ds_scope, { ProductCard });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/content/ProductCard.jsx", error: String((e && e.message) || e) }); }

// components/layout/PageHeader.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Loop X page header — the document header bar used across brand
 * collateral and slides. Mono labels over a hairline rule: a left
 * label, a section label, and an index/page marker.
 */
function PageHeader({
  left = "LOOP X",
  section = "BRAND GUIDELINES",
  index = "",
  tone = "dark",
  // "dark" ink on light | "light" ink on dark
  className,
  style,
  ...rest
}) {
  const ink = tone === "light" ? "var(--lx-off-white)" : "var(--lx-black)";
  const rule = tone === "light" ? "var(--hairline-dark)" : "var(--lx-black)";
  const label = {
    fontFamily: "var(--font-mono)",
    fontSize: 12,
    letterSpacing: "0.04em",
    textTransform: "uppercase",
    color: ink,
    lineHeight: 1
  };
  return /*#__PURE__*/React.createElement("div", _extends({
    className: className,
    style: {
      display: "grid",
      gridTemplateColumns: "1fr 1fr",
      columnGap: 40,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: `1px solid ${rule}`,
      paddingTop: 10
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: label
  }, left)), /*#__PURE__*/React.createElement("div", {
    style: {
      borderTop: `1px solid ${rule}`,
      paddingTop: 10,
      display: "flex",
      justifyContent: "space-between"
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: label
  }, section), index !== "" && /*#__PURE__*/React.createElement("span", {
    style: label
  }, index)));
}
Object.assign(__ds_scope, { PageHeader });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/PageHeader.jsx", error: String((e && e.message) || e) }); }

// components/layout/Panel.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Loop X panel — the signature chamfered container. Optional hairline
 * border and tone. This is the building block for cards, framed media,
 * and content blocks throughout the system. Corners are cut, never
 * rounded (the system is overwhelmingly square-edged).
 */
function Panel({
  children,
  tone = "light",
  // "light" | "dark" | "muted" | "grey" | "none"
  bordered = false,
  chamfer = 14,
  padding = 24,
  className,
  style,
  ...rest
}) {
  const bg = {
    light: "var(--lx-white)",
    dark: "var(--lx-black)",
    muted: "var(--lx-off-white)",
    grey: "var(--lx-grey)",
    none: "transparent"
  }[tone];
  const onDark = tone === "dark";
  const borderColor = onDark ? "var(--lx-off-white)" : "var(--lx-black)";
  return /*#__PURE__*/React.createElement("div", _extends({
    className: `lx-chamfer ${className || ""}`,
    style: {
      position: "relative",
      background: bg,
      color: onDark ? "var(--lx-off-white)" : "var(--lx-black)",
      padding,
      border: bordered ? `1px solid ${borderColor}` : "none",
      ["--chamfer"]: `${chamfer}px`,
      ...style
    }
  }, rest), children);
}
Object.assign(__ds_scope, { Panel });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/layout/Panel.jsx", error: String((e && e.message) || e) }); }

// components/navigation/Navbar.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/**
 * Loop X site navigation — the wordmark with a row of chamfered mono
 * nav items. The active item reads as a solid chamfered pill; the
 * rest are hairline-framed. Sits over a hairline rule on the hero.
 */
function Navbar({
  items = ["HOME", "PRODUCT", "ABOUT", "SOLUTIONS"],
  active = "SOLUTIONS",
  tone = "light",
  // "light" = on dark hero | "dark" = on light bg
  onSelect,
  className,
  style,
  ...rest
}) {
  const onDark = tone === "light";
  const ink = onDark ? "var(--lx-off-white)" : "var(--lx-black)";
  const paper = onDark ? "var(--lx-black)" : "var(--lx-off-white)";
  const rule = onDark ? "var(--hairline-dark)" : "var(--hairline-light)";
  return /*#__PURE__*/React.createElement("nav", _extends({
    className: className,
    style: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      paddingBottom: 14,
      borderBottom: `1px solid ${rule}`,
      color: ink,
      ...style
    }
  }, rest), /*#__PURE__*/React.createElement(__ds_scope.Logo, {
    height: 22,
    tone: ink
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "flex",
      gap: 8
    }
  }, items.map(item => {
    const isActive = item === active;
    return /*#__PURE__*/React.createElement("button", {
      key: item,
      onClick: () => onSelect && onSelect(item),
      className: "lx-chamfer",
      style: {
        ["--chamfer"]: "6px",
        fontFamily: "var(--font-mono)",
        fontSize: 11,
        letterSpacing: "0.04em",
        textTransform: "uppercase",
        padding: "8px 14px",
        cursor: "pointer",
        color: isActive ? paper : ink,
        background: isActive ? ink : "transparent",
        border: isActive ? "none" : `1px solid ${ink}`,
        transition: "opacity var(--dur-fast) var(--ease-standard)"
      },
      onMouseEnter: e => e.currentTarget.style.opacity = "0.62",
      onMouseLeave: e => e.currentTarget.style.opacity = "1"
    }, item);
  })));
}
Object.assign(__ds_scope, { Navbar });
})(); } catch (e) { __ds_ns.__errors.push({ path: "components/navigation/Navbar.jsx", error: String((e && e.message) || e) }); }

// ui_kits/website/screens.jsx
try { (() => {
function _extends() { return _extends = Object.assign ? Object.assign.bind() : function (n) { for (var e = 1; e < arguments.length; e++) { var t = arguments[e]; for (var r in t) ({}).hasOwnProperty.call(t, r) && (n[r] = t[r]); } return n; }, _extends.apply(null, arguments); }
/* Loop X — Website UI kit screens.
   Composes design-system components from window.LoopXDesignSystem_d0e166.
   Recreation of the marketing site: dark hero, product grid, footer. */
const {
  Logo,
  Navbar,
  Button,
  ProductCard,
  Eyebrow
} = window.LoopXDesignSystem_d0e166;
const IMG = "../../assets/img";

/* ---- Hero (Home) ---------------------------------------------------- */
function Hero({
  nav
}) {
  return /*#__PURE__*/React.createElement("section", {
    style: {
      position: "relative",
      height: "100%",
      background: "var(--lx-black)",
      color: "var(--lx-off-white)",
      overflow: "hidden"
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: `${IMG}/thermal-vehicle.png`,
    alt: "",
    style: {
      position: "absolute",
      inset: 0,
      width: "100%",
      height: "78%",
      objectFit: "cover",
      opacity: 0.85,
      filter: "grayscale(1) contrast(1.08)"
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "absolute",
      inset: 0,
      background: "linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,.65) 72%, #000 100%)"
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "relative",
      padding: "36px 56px 0"
    }
  }, nav), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "relative",
      padding: "0 56px",
      marginTop: 64,
      maxWidth: 720
    }
  }, /*#__PURE__*/React.createElement("h1", {
    className: "lx-h1",
    style: {
      margin: 0,
      fontSize: 68,
      lineHeight: 0.92
    }
  }, "All condition", /*#__PURE__*/React.createElement("br", null), "intelligence"), /*#__PURE__*/React.createElement("p", {
    style: {
      fontFamily: "var(--font-primary)",
      fontSize: 16,
      lineHeight: 1.35,
      maxWidth: 380,
      opacity: 0.85,
      marginTop: 20
    }
  }, "Thermal perception that works in any condition \u2014 no tag, no map, and no light required."), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 24
    }
  }, /*#__PURE__*/React.createElement(Button, {
    tone: "light",
    arrow: true
  }, "More info"))), /*#__PURE__*/React.createElement("div", {
    style: {
      position: "absolute",
      left: 40,
      right: 40,
      bottom: 24
    }
  }, /*#__PURE__*/React.createElement(Logo, {
    height: 132,
    tone: "var(--lx-off-white)",
    style: {
      width: "100%",
      height: "auto"
    }
  })));
}

/* ---- Products (Solutions) ------------------------------------------- */
const PRODUCTS = [{
  title: "Collision Avoidance System",
  description: "The industry's first safety solution for underground and surface mining, fusing Vision AI, LiDAR and RF into one platform — 360° detection, proactive warnings and automatic intervention."
}, {
  title: "Load Sight System",
  description: "Volumetric load intelligence for haul cycles. See payload, spillage and fill in real time, in dust and total dark."
}, {
  title: "LoopX SLAM",
  description: "LiDAR, GPS, satellite imagery and inertial sensors fused for precise vehicle localization and mapping where GPS fails."
}];
function Products({
  nav
}) {
  return /*#__PURE__*/React.createElement("section", {
    style: {
      height: "100%",
      background: "var(--lx-off-white)",
      color: "var(--lx-black)",
      overflow: "auto"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "36px 56px 0"
    }
  }, nav), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "48px 56px 56px"
    }
  }, /*#__PURE__*/React.createElement(Eyebrow, null, "Platform"), /*#__PURE__*/React.createElement("h2", {
    className: "lx-h1",
    style: {
      margin: "16px 0 40px",
      fontSize: 52
    }
  }, "Machine intelligence for", /*#__PURE__*/React.createElement("br", null), "uncontrolled environments"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: "grid",
      gridTemplateColumns: "repeat(3, 1fr)",
      gap: 20
    }
  }, PRODUCTS.map(p => /*#__PURE__*/React.createElement(ProductCard, _extends({
    key: p.title
  }, p))))));
}

/* ---- About ---------------------------------------------------------- */
function About({
  nav
}) {
  return /*#__PURE__*/React.createElement("section", {
    style: {
      height: "100%",
      background: "var(--lx-black)",
      color: "var(--lx-off-white)",
      overflow: "auto"
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "36px 56px 0"
    }
  }, nav), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "56px 56px",
      display: "grid",
      gridTemplateColumns: "1fr 1.3fr",
      gap: 56,
      alignItems: "start"
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Eyebrow, {
    tone: "light"
  }, "Shared belief"), /*#__PURE__*/React.createElement("h2", {
    className: "lx-h2",
    style: {
      margin: "16px 0 0",
      fontSize: 34
    }
  }, "The most dangerous environments deserve the most intelligence")), /*#__PURE__*/React.createElement("div", {
    style: {
      fontFamily: "var(--font-primary)",
      fontSize: 18,
      lineHeight: 1.5,
      opacity: 0.9
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      marginTop: 0
    }
  }, "The most advanced machine vision has always been built for the easy places \u2014 the warehouse, the highway, the sunlit road \u2014 leaving the people in the hardest, most dangerous conditions in the blind spot."), /*#__PURE__*/React.createElement("p", null, "So we started where it's hardest, on the principle that autonomy is won in the dark. Build perception there, and the ladder builds itself."), /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 24
    }
  }, /*#__PURE__*/React.createElement(Button, {
    tone: "light",
    variant: "ghost",
    arrow: true
  }, "Our strategy")))), /*#__PURE__*/React.createElement("div", {
    style: {
      padding: "0 56px 48px"
    }
  }, /*#__PURE__*/React.createElement("img", {
    src: `${IMG}/thermal-terrain.png`,
    alt: "",
    className: "lx-chamfer",
    style: {
      "--chamfer": "16px",
      width: "100%",
      height: 300,
      objectFit: "cover",
      filter: "grayscale(1) contrast(1.05)"
    }
  })));
}
window.LoopXSite = {
  Hero,
  Products,
  About
};
})(); } catch (e) { __ds_ns.__errors.push({ path: "ui_kits/website/screens.jsx", error: String((e && e.message) || e) }); }

__ds_ns.Logo = __ds_scope.Logo;

__ds_ns.Eyebrow = __ds_scope.Eyebrow;

__ds_ns.ProductCard = __ds_scope.ProductCard;

__ds_ns.Button = __ds_scope.Button;

__ds_ns.PageHeader = __ds_scope.PageHeader;

__ds_ns.Panel = __ds_scope.Panel;

__ds_ns.Navbar = __ds_scope.Navbar;

})();
