import { FC } from "react";
import { MemoizedReactMarkdown } from "./ui/markdown";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";
import "katex/dist/katex.min.css";

export interface MessageProps {
  message: string;
}

export const MessageComponent: FC<MessageProps> = ({ message }) => {
  return (
    <MemoizedReactMarkdown
      remarkPlugins={[remarkMath]}
      rehypePlugins={[rehypeKatex]}
      className="prose-base prose-neutral"
    >
      {message}
    </MemoizedReactMarkdown>
  );
};
