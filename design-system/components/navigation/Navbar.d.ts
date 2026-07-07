import * as React from "react";

/**
 * Loop X site navigation — wordmark + chamfered mono nav items.
 *
 */
export interface NavbarProps extends React.HTMLAttributes<HTMLElement> {
  /** Nav item labels. Default HOME / PRODUCT / ABOUT / SOLUTIONS. */
  items?: string[];
  /** Which item reads as the solid active pill. */
  active?: string;
  /** "light" over a dark hero, "dark" over a light background. Default "light". */
  tone?: "light" | "dark";
  /** Called with the item label on click. */
  onSelect?: (item: string) => void;
}

export function Navbar(props: NavbarProps): JSX.Element;
