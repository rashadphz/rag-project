"use client";
import { Source } from "@/interfaces";
import { useState } from "react";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";

export interface SearchResultsProps {
  results: { filename: string; content: string }[];
}
export function SearchResults({ results }: SearchResultsProps) {
  const [showAll, setShowAll] = useState(false);

  const displayedResults = showAll ? results : results.slice(0, 3);
  const additionalCount = results.length > 3 ? results.length - 3 : 0;
  return (
    <div className="flex flex-wrap ">
      {displayedResults.map(({ filename, content }, index) => (
        <div key={`source-${index}`} className="w-1/2 md:w-1/4 p-1">
          <Card className="flex-1 rounded-md flex-col h-full shadow-none border-none">
            <CardContent className="p-2">
              <p className="text-xs line-clamp-2 font-medium text-foreground/80">
                {content}
              </p>
              <div className="mt-2 flex items-center space-x-2">
                <div className="text-xs text-muted-foreground truncate">
                  {filename}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      ))}
      {!showAll && additionalCount > 0 && (
        <div className="w-1/2 md:w-1/4  p-1">
          <Card className="flex-1 rounded-md flex h-full items-center justify-center shadow-none border-none">
            <CardContent className="p-2">
              <Button
                variant="link"
                className="text-muted-foreground"
                onClick={() => setShowAll(true)}
              >
                View {additionalCount} more
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
