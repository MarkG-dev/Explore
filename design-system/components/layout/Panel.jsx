import React from "react";

/**
 * Loop X panel — the signature chamfered container. Optional hairline
 * border and tone. This is the building block for cards, framed media,
 * and content blocks throughout the system. Corners are cut, never
 * rounded (the system is overwhelmingly square-edged).
 */
export function Panel({
  children,
  tone = "light",        // "light" | "dark" | "muted" | "grey" | "none"
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
    none: "transparent",
  }[tone];

  const onDark = tone === "dark";
  const borderColor = onDark ? "var(--lx-off-white)" : "var(--lx-black)";

  return (
    <div
      className={`lx-chamfer ${className || ""}`}
      style={{
        position: "relative",
        background: bg,
        color: onDark ? "var(--lx-off-white)" : "var(--lx-black)",
        padding,
        border: bordered ? `1px solid ${borderColor}` : "none",
        ["--chamfer"]: `${chamfer}px`,
        ...style,
      }}
      {...rest}
    >
      {children}
    </div>
  );
}
