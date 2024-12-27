<script lang="ts">
  import { marked } from "marked";
  import DOMPurify from "isomorphic-dompurify";
  import { onMount } from "svelte";
  import { SOURCE_DELIMITER } from "$lib/constants";

  enum ChatCompletionRequestMessageRoleEnum {
    user = "user",
    assistant = "assistant",
    system = "system",
  }

  export let type: ChatCompletionRequestMessageRoleEnum;
  export let message: string = "";
  export { classes as class };

  let classes = "";
  let scrollToDiv: HTMLDivElement;

  const classSet = {
    user: "justify-end",
    assistant: "justify-start",
    system: "justify-center text-gray-400",
  };

  const messageClasses = {
    user: "bg-gray-100 text-[#333333]",
    assistant: "text-[#333333]",
    system: "bg-gray-100 text-[#666666]",
  };

  const typeEffect = (node: HTMLDivElement, message: string) => {
    return {
      update(message: string) {
        scrollToDiv.scrollIntoView({
          behavior: "auto",
          block: "end",
          inline: "end",
        });
      },
    };
  };

  onMount(() => {
    scrollToDiv.scrollIntoView({
      behavior: "auto",
      block: "end",
      inline: "end",
    });
  });

  // Configure marked options for better formatting
  marked.setOptions({
    gfm: true, // GitHub Flavored Markdown
    breaks: true, // Convert \n to <br>
  });

  // Function to parse message and format with superscript numbers
  function formatMessageWithSources(message: string) {
    let sourceCount = 0;

    const formattedMessage = message.replace(new RegExp(`${SOURCE_DELIMITER}([^${SOURCE_DELIMITER}]+)${SOURCE_DELIMITER}`, 'g'), (fullMatch, url) => {
        sourceCount++;
        return `<a href="${url}" target="_blank" rel="noopener noreferrer"
                  class="inline-flex items-center justify-center w-5 h-5 text-xs
                         align-top rounded-full bg-[#dd1c1a]/10 text-[#dd1c1a]
                         hover:bg-[#dd1c1a]/20 transition-colors duration-200
                         no-underline ml-0.5">${sourceCount}</a>`;
    });

    return formattedMessage;
  }

  $: formattedMessage = formatMessageWithSources(message);
</script>

<div class="flex {classSet[type]}">
  <div
    use:typeEffect={message}
    class="max-w-[100%] rounded-lg px-4 py-3 min-h-[2rem] break-words {classes} {messageClasses[type]}"
  >
      <div class="prose prose-sm dark:prose-invert max-w-none
                  prose-headings:mb-2 prose-headings:mt-4 first:prose-headings:mt-0
                  prose-p:my-2 prose-p:leading-relaxed
                  prose-li:my-0.5
                  prose-code:px-1 prose-code:py-0.5 prose-code:bg-gray-100 prose-code:rounded
                  prose-pre:bg-gray-100 prose-pre:p-3 prose-pre:rounded-lg
                  dark:prose-code:bg-gray-800 dark:prose-pre:bg-gray-800">
        {@html DOMPurify.sanitize(marked.parse(formattedMessage).toString())}
      </div>
  </div>
  <div bind:this={scrollToDiv} />
</div>
