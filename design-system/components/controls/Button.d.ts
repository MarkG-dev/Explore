import * as React from "react";

/**
 * Loop X button — chamfered, DM Mono, uppercase control.
 *
 */
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /** Visual style. Default "outline". */
  variant?: "outline" | "solid" | "ghost";
  /** "dark" for light backgrounds, "light" for dark backgrounds. Default "dark". */
  tone?: "dark" | "light";
  /** Default "md". */
  size?: "sm" | "md" | "lg";
  /** Show the trailing arrow glyph. Default false. */
  arrow?: boolean;
  /** Element/tag to render. Default "button". Use "a" for links. */
  as?: React.ElementType;
}

export function Button(props: ButtonProps): JSX.Element;
