import React from "react";

/**
 * Loop X page header — the document header bar used across brand
 * collateral and slides. Mono labels over a hairline rule: a left
 * label, a section label, and an index/page marker.
 */
export function PageHeader({
  left = "LOOP X",
  section = "BRAND GUIDELINES",
  index = "",
  tone = "dark", // "dark" ink on light | "light" ink on dark
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
    lineHeight: 1,
  };

  return (
    <div
      className={className}
      style={{ display: "grid", gridTemplateColumns: "1fr 1fr", columnGap: 40, ...style }}
      {...rest}
    >
      <div style={{ borderTop: `1px solid ${rule}`, paddingTop: 10 }}>
        <span style={label}>{left}</span>
      </div>
      <div style={{ borderTop: `1px solid ${rule}`, paddingTop: 10, display: "flex", justifyContent: "space-between" }}>
        <span style={label}>{section}</span>
        {index !== "" && <span style={label}>{index}</span>}
      </div>
    </div>
  );
}
