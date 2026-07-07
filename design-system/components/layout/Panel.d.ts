import * as React from "react";

/**
 * Loop X panel — signature chamfered container / card.
 *
 */
export interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Surface tone. Default "light". */
  tone?: "light" | "dark" | "muted" | "grey" | "none";
  /** Draw the hairline border. Default false. */
  bordered?: boolean;
  /** Cut-corner size in px. Default 14. */
  chamfer?: number;
  /** Inner padding in px. Default 24. */
  padding?: number;
}

export function Panel(props: PanelProps): JSX.Element;
