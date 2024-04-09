"use client";
import {
  Bird,
  Book,
  Bot,
  Code2,
  CornerDownLeft,
  LifeBuoy,
  Mic,
  Paperclip,
  PlusCircleIcon,
  Rabbit,
  Settings,
  Settings2,
  Share,
  SquareTerminal,
  SquareUser,
  Triangle,
  Turtle,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useEffect, useState } from "react";
import { sendMessage } from "@/lib";
import {
  FollowUpQuestions,
  Source,
  SourceResponse,
  TextChunk,
} from "@/interfaces";
import { Card, CardContent } from "@/components/ui/card";

const SourceBox: React.FC<Source> = ({ name, url }) => (
  <div>
    <a href={url} target="_blank" rel="noopener noreferrer">
      {name}
    </a>
  </div>
);

const TextChunkComponent: React.FC<TextChunk> = ({ text }) => (
  <></>
  //   <div>{text}</div>
);

const FollowUpQuestionBox: React.FC<{ question: string }> = ({ question }) => (
  <li>{question}</li>
);

export default function Dashboard() {
  const [sourceResponses, setSourceResponses] = useState<Source[]>([]);
  const [textChunks, setTextChunks] = useState<TextChunk[]>([]);
  const [followUpQuestions, setFollowUpQuestions] = useState<string[]>([]);

  const onSubmit = async () => {
    for await (const packet of sendMessage({ message: "Who made this?" })) {
      if (Object.hasOwn(packet, "top_sources")) {
        console.log(packet as SourceResponse);
        setSourceResponses((packet as SourceResponse).top_sources);
      } else if (Object.hasOwn(packet, "text")) {
        setTextChunks((prev) => [...prev, packet as TextChunk]);
      } else if (Object.hasOwn(packet, "questions")) {
        setFollowUpQuestions((packet as FollowUpQuestions).questions);
      }
    }
  };
  return (
    <div className="grid h-screen w-full">
      <div className="flex flex-col">
        <header className="sticky top-0 z-10 flex h-[53px] items-center gap-1 border-b bg-background px-4">
          <h1 className="text-xl font-semibold">Playground</h1>
          <Drawer>
            <DrawerTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden">
                <Settings className="size-4" />
                <span className="sr-only">Settings</span>
              </Button>
            </DrawerTrigger>
            <DrawerContent className="max-h-[80vh]">
              <DrawerHeader>
                <DrawerTitle>Configuration</DrawerTitle>
                <DrawerDescription>
                  Configure the settings for the model and messages.
                </DrawerDescription>
              </DrawerHeader>
              <form className="grid w-full items-start gap-6 overflow-auto p-4 pt-0">
                <fieldset className="grid gap-6 rounded-lg border p-4">
                  <legend className="-ml-1 px-1 text-sm font-medium">
                    Settings
                  </legend>
                  <div className="grid gap-3">
                    <Label htmlFor="model">Model</Label>
                    <Select>
                      <SelectTrigger
                        id="model"
                        className="items-start [&_[data-description]]:hidden"
                      >
                        <SelectValue placeholder="Select a model" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="genesis">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <Rabbit className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                <span className="font-medium text-foreground">
                                  GPT-4
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                Our fastest model for general use cases.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                        <SelectItem value="explorer">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <Bird className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                Neural{" "}
                                <span className="font-medium text-foreground">
                                  Explorer
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                Performance and speed for efficiency.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                        <SelectItem value="quantum">
                          <div className="flex items-start gap-3 text-muted-foreground">
                            <Turtle className="size-5" />
                            <div className="grid gap-0.5">
                              <p>
                                Neural{" "}
                                <span className="font-medium text-foreground">
                                  Quantum
                                </span>
                              </p>
                              <p className="text-xs" data-description>
                                The most powerful model for complex
                                computations.
                              </p>
                            </div>
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="temperature">Temperature</Label>
                    <Input id="temperature" type="number" placeholder="0.4" />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="top-p">Top P</Label>
                    <Input id="top-p" type="number" placeholder="0.7" />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="top-k">Top K</Label>
                    <Input id="top-k" type="number" placeholder="0.0" />
                  </div>
                </fieldset>
                <fieldset className="grid gap-6 rounded-lg border p-4">
                  <legend className="-ml-1 px-1 text-sm font-medium">
                    Messages
                  </legend>
                  <div className="grid gap-3">
                    <Label htmlFor="role">Role</Label>
                    <Select defaultValue="system">
                      <SelectTrigger>
                        <SelectValue placeholder="Select a role" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="system">System</SelectItem>
                        <SelectItem value="user">User</SelectItem>
                        <SelectItem value="assistant">Assistant</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="content">Content</Label>
                    <Textarea id="content" placeholder="You are a..." />
                  </div>
                </fieldset>
              </form>
            </DrawerContent>
          </Drawer>
        </header>
        <main className="grid flex-1 gap-4 overflow-auto p-4 md:grid-cols-2 lg:grid-cols-3">
          <div
            className="relative hidden flex-col items-start gap-8 md:flex"
            x-chunk="dashboard-03-chunk-0"
          >
            <form className="grid w-full items-start gap-6">
              <fieldset className="grid gap-6 rounded-lg border p-4">
                <legend className="-ml-1 px-1 text-sm font-medium">
                  Settings
                </legend>
                <div className="grid gap-3">
                  <Label htmlFor="model">Model</Label>
                  <Select defaultValue="gpt4">
                    <SelectTrigger
                      id="model"
                      className="items-start [&_[data-description]]:hidden"
                    >
                      <SelectValue placeholder="Select a model" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gpt4">
                        <div className="flex items-start gap-3 text-muted-foreground">
                          <Turtle className="size-5" />
                          <div className="grid gap-0.5">
                            <p>
                              <span className="font-medium text-foreground">
                                GPT-4 Turbo
                              </span>
                            </p>
                            <p className="text-xs" data-description>
                              Slower, but more accurate.
                            </p>
                          </div>
                        </div>
                      </SelectItem>
                      <SelectItem value="gpt3">
                        <div className="flex items-start gap-3 text-muted-foreground">
                          <Rabbit className="size-5" />
                          <div className="grid gap-0.5">
                            <p>
                              <span className="font-medium text-foreground">
                                GPT-3.5 Turbo
                              </span>
                            </p>
                            <p className="text-xs" data-description>
                              Fast, but less accurate.
                            </p>
                          </div>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-3">
                  <Label htmlFor="temperature">Temperature</Label>
                  <Input id="temperature" type="number" placeholder="0.4" />
                </div>
                {/* <div className="grid grid-cols-2 gap-4">
                  <div className="grid gap-3">
                    <Label htmlFor="top-p">Top P</Label>
                    <Input id="top-p" type="number" placeholder="0.7" />
                  </div>
                  <div className="grid gap-3">
                    <Label htmlFor="top-k">Top K</Label>
                    <Input id="top-k" type="number" placeholder="0.0" />
                  </div> */}
                {/* </div> */}
              </fieldset>
              {/* <fieldset className="grid gap-6 rounded-lg border p-4">
                <legend className="-ml-1 px-1 text-sm font-medium">
                  Messages
                </legend>
                <div className="grid gap-3">
                  <Label htmlFor="role">Role</Label>
                  <Select defaultValue="system">
                    <SelectTrigger>
                      <SelectValue placeholder="Select a role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="system">System</SelectItem>
                      <SelectItem value="user">User</SelectItem>
                      <SelectItem value="assistant">Assistant</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid gap-3">
                  <Label htmlFor="content">Content</Label>
                  <Textarea
                    id="content"
                    placeholder="You are a..."
                    className="min-h-[9.5rem]"
                  />
                </div>
              </fieldset> */}
            </form>
          </div>
          <div className="relative flex h-full min-h-[50vh] flex-col rounded-md p-4 lg:col-span-2">
            {/* <Badge variant="outline" className="absolute right-3 top-3">
              Output
            </Badge> */}
            <div className="flex-1">
              <div className="flex flex-col gap-4">
                {/* Query */}
                <div className="text-2xl">
                  How do local balanced samplers in generative models compare in
                  terms of sample quality and diversity?
                </div>
                {/* Sources */}
                {sourceResponses.length > 0 && (
                  <div>
                    <div className="text-lg font-medium">Sources</div>
                    <div className="flex flex-wrap ">
                      {sourceResponses.map(({ name, url }, index) => (
                        <div
                          key={`source-${index}`}
                          className="w-1/2 md:w-1/4  pl-0 p-2"
                        >
                          <Card className="flex-1 rounded-md">
                            <CardContent className="p-2">
                              <p className="text-xs line-clamp-2">{name}</p>
                              <div className="mt-2 flex items-center space-x-2">
                                <div className="text-xs opacity-60 truncate">
                                  {url}
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                {/* Answer */}
                {textChunks.length > 0 && (
                  <div>
                    <div className="text-lg font-medium">Answer</div>
                    <div>{textChunks.map(({ text }) => text).join(" ")}</div>
                  </div>
                )}
                {/* Related */}
                {followUpQuestions.length > 0 && (
                  <div className="mt-4">
                    <div className="flex items-center text-lg font-medium">
                      Related
                    </div>
                    <div className="divide-y border-t mt-2">
                      {followUpQuestions.map((question, index) => (
                        <div
                          key={`question-${index}`}
                          className="flex cursor-pointer items-center py-2 font-medium"
                        >
                          <PlusCircleIcon className="mr-2" size={16} />{" "}
                          {question}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="relative overflow-hidden rounded-lg border bg-background focus-within:ring-1 focus-within:ring-ring">
              <Label htmlFor="message" className="sr-only">
                Message
              </Label>
              <Textarea
                id="message"
                placeholder="Type your message here..."
                className="min-h-12 resize-none border-0 p-3 shadow-none focus-visible:ring-0"
              />
              <div className="flex items-center p-3 pt-0">
                <Button
                  onClick={onSubmit}
                  size="sm"
                  className="ml-auto gap-1.5"
                >
                  Send Message
                  <CornerDownLeft className="size-3.5" />
                </Button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
