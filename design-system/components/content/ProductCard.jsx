import React from "react";
import { Button } from "../controls/Button.jsx";

/**
 * Loop X product card — a chamfered, hairline-framed block pairing a
 * title, short description and a "more info" action. Matches the
 * product tiles used on the site and in decks.
 */
export function ProductCard({
  title,
  description,
  action = "MORE INFO",
  tone = "light", // "light" | "dark"
  onAction,
  className,
  style,
  ...rest
}) {
  const onDark = tone === "dark";
  const ink = onDark ? "var(--lx-off-white)" : "var(--lx-black)";
  return (
    <div
      className={`lx-chamfer ${className || ""}`}
      style={{
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
        ...style,
      }}
      {...rest}
    >
      <h3
        style={{
          margin: 0,
          fontFamily: "var(--font-primary)",
          fontWeight: 400,
          fontSize: 30,
          lineHeight: 0.9,
          textTransform: "uppercase",
        }}
      >
        {title}
      </h3>
      <p
        style={{
          margin: 0,
          fontFamily: "var(--font-primary)",
          fontWeight: 400,
          fontSize: 14,
          lineHeight: 1.35,
          opacity: 0.82,
          flex: "0 1 auto",
        }}
      >
        {description}
      </p>
      <div>
        <Button size="sm" tone={onDark ? "light" : "dark"} arrow onClick={onAction}>
          {action}
        </Button>
      </div>
    </div>
  );
}
