import React from "react";

/**
 * Loop X button — the signature chamfered ("cut corner") control.
 * DM Mono, uppercase. Outline by default; solid for primary emphasis.
 * The chamfer echoes the notched LOOP X letterforms.
 */
export function Button({
  children,
  variant = "outline", // "outline" | "solid" | "ghost"
  tone = "dark",       // "dark" (on light bg) | "light" (on dark bg)
  size = "md",         // "sm" | "md" | "lg"
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
    sm: { padding: "7px 14px", fontSize: 11, chamfer: 5 },
    md: { padding: "11px 20px", fontSize: 12, chamfer: 7 },
    lg: { padding: "15px 28px", fontSize: 14, chamfer: 9 },
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
    ...style,
  };

  return (
    <Tag
      className={`lx-chamfer ${className || ""}`}
      style={base}
      onMouseEnter={(e) => (e.currentTarget.style.opacity = "0.62")}
      onMouseLeave={(e) => (e.currentTarget.style.opacity = "1")}
      {...rest}
    >
      {children}
      {arrow && (
        <svg width="13" height="10" viewBox="0 0 13 10" fill="none" aria-hidden="true" style={{ flexShrink: 0 }}>
          <path d="M8 1L12 5L8 9" stroke="currentColor" strokeWidth="1.3" />
          <path d="M0 5H12" stroke="currentColor" strokeWidth="1.3" />
        </svg>
      )}
    </Tag>
  );
}
