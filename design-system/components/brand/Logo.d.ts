import * as React from "react";

/**
 * Loop X logo — official wordmark and standalone symbol.
 * Paints in currentColor. Never alter, recolour internally, or distort.
 *
 */
export interface LogoProps extends React.SVGProps<SVGSVGElement> {
  /** "wordmark" (default) = full LOOP X lockup; "symbol" = the X mark only (favicons, avatars). */
  variant?: "wordmark" | "symbol";
  /** Rendered height in px; width derives from the mark's aspect ratio. Default 40. */
  height?: number;
  /** Convenience colour override (sets currentColor). Defaults to inherited color. */
  tone?: string;
  /** Accessible label. Default "Loop X". */
  title?: string;
}

export function Logo(props: LogoProps): JSX.Element;
