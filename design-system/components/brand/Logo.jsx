import React from "react";

/**
 * Loop X logo — the official wordmark and the standalone symbol (X).
 * Vector artwork transcribed verbatim from the brand file. Paints in
 * `currentColor`, so set `color` (or the `tone` prop) on/around it.
 * Never redraw, recolour internally, stretch, or decorate the mark.
 */
const WORDMARK = [
  // L
  { x: 0, w: 307.285, d: "M 53.486 178.813 L 53.486 0 L 0 0 L 0 199.263 L 46.67 245.933 L 307.285 245.933 L 307.285 192.446 L 67.645 192.446 L 53.486 178.813 Z" },
  // O
  { x: 339.797, w: 323.541, d: "M 46.67 0 L 0 46.67 L 0 199.263 L 46.67 245.933 L 276.871 245.933 L 323.541 199.263 L 323.541 46.67 L 276.871 0 L 46.67 0 Z M 270.054 177.764 L 255.372 192.446 L 68.693 192.446 L 53.486 177.239 L 53.486 68.693 L 68.169 53.486 L 254.847 53.486 L 270.054 68.169 L 270.054 177.239 L 270.054 177.764 Z" },
  // O
  { x: 701.09, w: 323.541, d: "M 46.67 0 L 0 46.67 L 0 199.263 L 46.67 245.933 L 276.871 245.933 L 323.541 199.263 L 323.541 46.67 L 276.871 0 L 46.67 0 Z M 270.054 177.764 L 255.372 192.446 L 68.693 192.446 L 53.486 177.239 L 53.486 68.693 L 68.169 53.486 L 254.847 53.486 L 270.054 68.169 L 270.054 177.239 L 270.054 177.764 Z" },
  // P
  { x: 1062.392, w: 323.541, d: "M 46.67 0 L 0 46.67 L 0 245.933 L 53.486 245.933 L 53.486 181.959 L 276.871 181.959 L 323.541 135.289 L 323.541 46.67 L 276.871 0 L 46.67 0 Z M 270.054 114.314 L 255.896 128.997 L 54.011 128.997 L 54.011 68.693 L 68.693 54.011 L 255.896 54.011 L 270.579 68.693 L 270.579 114.839 L 270.054 114.314 Z" },
  // X
  { x: 1498.136, w: 323.541, d: "M 0 246.457 L 15.207 246.457 L 111.168 149.972 L 211.848 149.972 L 307.809 246.457 L 323.541 246.457 L 323.541 184.056 L 262.189 122.704 L 323.541 61.352 L 323.541 0 L 306.761 0 L 211.848 94.912 L 111.168 94.912 L 16.256 0 L 0 0 L 0 61.352 L 60.828 122.704 L 0 184.056 L 0 246.457 Z" },
];

const SYMBOL_PATH =
  "M 0 383.831 L 23.683 383.831 L 173.132 233.565 L 329.931 233.565 L 479.38 383.831 L 503.88 383.831 L 503.88 286.648 L 408.331 191.099 L 503.88 95.549 L 503.88 0 L 477.747 0 L 329.931 147.816 L 173.132 147.816 L 25.316 0 L 0 0 L 0 95.549 L 94.733 191.099 L 0 286.648 L 0 383.831 Z";

export function Logo({
  variant = "wordmark",
  height = 40,
  tone,
  title = "Loop X",
  className,
  style,
  ...rest
}) {
  const colorStyle = tone ? { color: tone } : null;

  if (variant === "symbol") {
    const w = height * (503.88 / 383.831);
    return (
      <svg
        role="img"
        aria-label={title}
        viewBox="0 0 503.88 383.831"
        width={w}
        height={height}
        className={className}
        style={{ display: "block", ...colorStyle, ...style }}
        {...rest}
      >
        <title>{title}</title>
        <path d={SYMBOL_PATH} fill="currentColor" fillRule="nonzero" />
      </svg>
    );
  }

  const VB_W = 1821.677;
  const VB_H = 246.457;
  const w = height * (VB_W / VB_H);
  return (
    <svg
      role="img"
      aria-label={title}
      viewBox={`0 0 ${VB_W} ${VB_H}`}
      width={w}
      height={height}
      className={className}
      style={{ display: "block", ...colorStyle, ...style }}
      {...rest}
    >
      <title>{title}</title>
      {WORDMARK.map((g, i) => (
        <path key={i} transform={`translate(${g.x} 0)`} d={g.d} fill="currentColor" fillRule="nonzero" />
      ))}
    </svg>
  );
}
