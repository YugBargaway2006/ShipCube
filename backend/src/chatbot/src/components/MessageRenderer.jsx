import React from "react";

export const MessageRenderer = ({ message }) => {
  if (!message) return null;

  const user = message.user || "bot";
  const text = message.reply || message.text || message.responseText || "[no content]";

  return (
    <div
      className={user === "bot" ? "bot-message" : "user-message"}
      dangerouslySetInnerHTML={{ __html: text }}
    ></div>
  );
};
