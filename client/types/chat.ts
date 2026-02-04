export type ChatMessage =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string }
  | { role: "assistant"; type: "emails"; emails: any[] }
  | {
      role: "assistant";
      type: "reply_preview";
      original_subject: string;
      reply: string;
    }
  | {
      role: "assistant";
      type: "confirm_delete";
      email: any;
    };
