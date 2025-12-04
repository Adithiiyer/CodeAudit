import React from "react";
import CodeMirror from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { javascript } from "@codemirror/lang-javascript";

export default function CodeEditor({ value, onChange }) {
  return (
    <CodeMirror
      value={value}
      height="350px"
      theme="dark"
      extensions={[python(), javascript()]}
      onChange={onChange}
    />
  );
}
