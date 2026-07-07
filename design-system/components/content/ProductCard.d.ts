import * as React from "react";

/**
 * Loop X product card — chamfered, hairline-framed title +
 * description + action block.
 *
 */
export interface ProductCardProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Card title (rendered uppercase). */
  title: string;
  /** Supporting description copy. */
  description: string;
  /** Action label. Default "MORE INFO". */
  action?: string;
  /** "light" (transparent/ink) or "dark" (black fill). Default "light". */
  tone?: "light" | "dark";
  /** Action click handler. */
  onAction?: () => void;
}

export function ProductCard(props: ProductCardProps): JSX.Element;
