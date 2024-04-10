import { ArrowRight, PlusCircleIcon } from "lucide-react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { useEffect, useRef, useState } from "react";
import {
  FollowUpQuestions,
  Source,
  SourceResponse,
  TextChunk,
} from "@/interfaces";
import { sendMessage } from "@/lib";
import { SearchResults } from "./search-results";
import { MessageComponent } from "./message";
import { AskInput } from "./ask-input";

const HumanMessage = ({ message }: { message: string }) => {
  return <div className="text-2xl">{message}</div>;
};

const AiMessage = ({
  message,
  sources,
  followUpQuestions,
  handleSubmit,
}: {
  message: string;
  sources: Source[];
  followUpQuestions: string[];
  handleSubmit?: (query: string) => Promise<void>;
}) => {
  return (
    <>
      {/* Sources */}
      {sources.length > 0 && (
        <div>
          <div className="text-lg font-medium">Sources</div>
          <SearchResults
            results={sources.map(({ filename, heading }) => ({
              filename,
              content: heading,
            }))}
          />
        </div>
      )}
      {/* Answer */}
      <div>
        <div className="text-lg font-medium">Answer</div>
        <MessageComponent message={message} />
      </div>
      {/* Related */}
      {followUpQuestions.length > 0 && (
        <div className="mt-4">
          <div className="flex items-center text-lg font-medium">Related</div>
          <div className="divide-y border-t mt-2">
            {followUpQuestions.map((question, index) => (
              <div
                key={`question-${index}`}
                onClick={(e) => handleSubmit?.(question)}
                className="flex cursor-pointer items-center py-2 font-medium"
              >
                <PlusCircleIcon className="mr-2" size={20} />{" "}
                {question.toLowerCase()}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

export interface Message {
  type: "user" | "assistant";
  message: string;
  sources?: Source[];
  followUpQuestions?: string[];
}

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const [showFollowUpPanel, setShowFollowUpPanel] = useState(false);

  const submitQuery = async (query: string) => {
    setShowFollowUpPanel(false);
    setMessages((prev) => [...prev, { type: "user", message: query }]);

    let answer = "";
    let sources: Source[] = [];
    let followUpQuestions: string[] = [];
    for await (const packet of sendMessage({ message: query })) {
      if (Object.hasOwn(packet, "top_sources")) {
        sources = (packet as SourceResponse).top_sources;
      } else if (Object.hasOwn(packet, "text")) {
        answer += (packet as TextChunk).text;
      } else if (Object.hasOwn(packet, "questions")) {
        followUpQuestions = (packet as FollowUpQuestions).questions;
      }

      // Update the AI message in real time
      setMessages((prev) => {
        // Remove the last assistant message if it exists
        const newMessages =
          prev.length > 0 && prev[prev.length - 1].type === "assistant"
            ? prev.slice(0, -1)
            : prev;
        // Add the updated assistant message
        return [
          ...newMessages,
          {
            type: "assistant",
            message: answer,
            sources: sources,
            followUpQuestions: followUpQuestions,
          },
        ];
      });
    }
    setShowFollowUpPanel(true);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setInput("");
    submitQuery(input);
  };

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  if (messages.length > 0) {
    return (
      <div className="relative flex h-full min-h-[50vh] flex-col rounded-md p-4 lg:col-span-2">
        <div className="flex-1">
          <div className="flex flex-col gap-4">
            {messages.map((message, index) => {
              if (message.type === "user") {
                return (
                  <HumanMessage
                    key={`message-${index}`}
                    message={message.message}
                  />
                );
              } else {
                return (
                  <AiMessage
                    key={`message-${index}`}
                    message={message.message}
                    sources={message.sources || []}
                    followUpQuestions={message.followUpQuestions || []}
                    handleSubmit={submitQuery}
                  />
                );
              }
            })}
          </div>
          {showFollowUpPanel && (
            <form className="w-full flex mt-8" onSubmit={handleSubmit}>
              <div className="relative flex items-center w-full">
                <AskInput
                  placeholder="Ask follow up"
                  inputRef={inputRef}
                  input={input}
                  setInput={setInput}
                />
              </div>
            </form>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bottom-10 flex justify-center items-center h-screen mx-auto">
      <form className="max-w-xl w-full px-7 flex" onSubmit={handleSubmit}>
        <div className="relative flex items-center w-full">
          <AskInput inputRef={inputRef} input={input} setInput={setInput} />
        </div>
      </form>
    </div>
  );
}
