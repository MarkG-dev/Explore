import React from "react";
import { Logo } from "../brand/Logo.jsx";

/**
 * Loop X site navigation — the wordmark with a row of chamfered mono
 * nav items. The active item reads as a solid chamfered pill; the
 * rest are hairline-framed. Sits over a hairline rule on the hero.
 */
export function Navbar({
  items = ["HOME", "PRODUCT", "ABOUT", "SOLUTIONS"],
  active = "SOLUTIONS",
  tone = "light", // "light" = on dark hero | "dark" = on light bg
  onSelect,
  className,
  style,
  ...rest
}) {
  const onDark = tone === "light";
  const ink = onDark ? "var(--lx-off-white)" : "var(--lx-black)";
  const paper = onDark ? "var(--lx-black)" : "var(--lx-off-white)";
  const rule = onDark ? "var(--hairline-dark)" : "var(--hairline-light)";

  return (
    <nav
      className={className}
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        paddingBottom: 14,
        borderBottom: `1px solid ${rule}`,
        color: ink,
        ...style,
      }}
      {...rest}
    >
      <Logo height={22} tone={ink} />
      <div style={{ display: "flex", gap: 8 }}>
        {items.map((item) => {
          const isActive = item === active;
          return (
            <button
              key={item}
              onClick={() => onSelect && onSelect(item)}
              className="lx-chamfer"
              style={{
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
                transition: "opacity var(--dur-fast) var(--ease-standard)",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.62")}
              onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
            >
              {item}
            </button>
          );
        })}
      </div>
    </nav>
  );
}
