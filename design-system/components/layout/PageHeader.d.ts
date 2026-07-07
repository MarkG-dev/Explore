import * as React from "react";

/** Loop X document header bar — mono labels over a hairline rule. */
export interface PageHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Left label. Default "LOOP X". */
  left?: string;
  /** Section label. Default "BRAND GUIDELINES". */
  section?: string;
  /** Right index / page marker. Default "". */
  index?: string;
  /** "dark" on light backgrounds, "light" on dark. Default "dark". */
  tone?: "dark" | "light";
}

export function PageHeader(props: PageHeaderProps): JSX.Element;
