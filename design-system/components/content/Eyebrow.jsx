import React from "react";

/**
 * Loop X eyebrow / label — DM Mono, uppercase, small. Optionally
 * wrapped in the signature chamfered hairline frame ("EYEBROW TEXT").
 * Used above headlines and to tag sections.
 */
export function Eyebrow({
  children,
  framed = false,
  tone = "dark", // "dark" ink on light | "light" ink on dark
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
    color: ink,
  };

  if (!framed) {
    return (
      <span className={className} style={{ ...label, ...style }} {...rest}>
        {children}
      </span>
    );
  }

  return (
    <span
      className={`lx-chamfer ${className || ""}`}
      style={{
        ...label,
        display: "inline-flex",
        alignItems: "center",
        padding: "6px 12px",
        border: `1px solid ${ink}`,
        ["--chamfer"]: "5px",
        ...style,
      }}
      {...rest}
    >
      {children}
    </span>
  );
}
