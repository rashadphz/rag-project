import { FC } from "react";
import { MemoizedReactMarkdown } from "./ui/markdown";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";
import "katex/dist/katex.min.css";

export interface MessageProps {
  message: string;
}

export const MessageComponent: FC<MessageProps> = ({ message }) => {
  const text = `Given a **formula** below
$$
s = ut + \\frac{1}{2}at^{2}
$$
Calculate the value of $s$ when $u = 10\\frac{m}{s}$ and $a = 2\\frac{m}{s^{2}}$ at $t = 1s$`;

  return (
    <MemoizedReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
      className="prose-base prose-neutral"
    >
      {message}
      {/* {text} */}
    </MemoizedReactMarkdown>
  );
};
