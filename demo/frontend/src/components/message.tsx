import { FC } from "react";
import { MemoizedReactMarkdown } from "./ui/markdown";

export interface MessageProps {
  message: string;
}

export const Message: FC<MessageProps> = ({ message }) => {
  return (
    <MemoizedReactMarkdown className="prose-base prose-neutral">
      {message}
    </MemoizedReactMarkdown>
  );
};
