import * as React from "react";

/**
 * Loop X eyebrow / label — DM Mono uppercase tag, optionally in a
 * chamfered hairline frame.
 */
export interface EyebrowProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Wrap in the chamfered hairline frame. Default false. */
  framed?: boolean;
  /** "dark" on light backgrounds, "light" on dark. Default "dark". */
  tone?: "dark" | "light";
}

export function Eyebrow(props: EyebrowProps): JSX.Element;
