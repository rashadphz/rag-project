import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { ArrowRight } from "lucide-react";
export function AskInput({
  input,
  setInput,
  inputRef,
  placeholder = "Ask anything...",
}: {
  input: string;
  setInput: (input: string) => void;
  inputRef: React.RefObject<HTMLInputElement>;
  placeholder?: string;
}) {
  return (
    <>
      <Input
        placeholder={placeholder}
        className="pl-6 pr-14 h-12 rounded-full flex-grow text-md"
        ref={inputRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <Button
        type="submit"
        variant="ghost"
        size="icon"
        className="absolute right-2"
        disabled={input.length === 0}
      >
        <ArrowRight size={20} />
      </Button>
    </>
  );
}
