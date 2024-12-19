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
  export let isLoading: boolean = false;
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

  // Function to parse message and format with superscript numbers
  function formatMessageWithSources(message: string) {
    let sourceCount = 0;
    
    // Replace entire &url& pattern (including delimiters) with numbered links
    const formattedMessage = message.replace(new RegExp(`${SOURCE_DELIMITER}([^${SOURCE_DELIMITER}]+)${SOURCE_DELIMITER}`, 'g'), (fullMatch, url) => {
      // fullMatch includes the & delimiters, url is just the content between them
      sourceCount++;
      return `<a href="${url}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center justify-center w-5 h-5 text-xs align-top rounded-full bg-blue-100 text-blue-700 hover:bg-blue-200 transition-colors duration-200 no-underline ml-0.5">${sourceCount}</a>`;
    });

    return formattedMessage;
  }

  $: formattedMessage = formatMessageWithSources(message);
</script>

<div class="flex {classSet[type]}">
  <div
    use:typeEffect={message}
    class="max-w-[85%] rounded-3xl px-4 py-2 min-h-[2rem] break-words {classes} {messageClasses[type]}"
  >
    {#if isLoading && type === 'assistant'}
      <div class="flex gap-1.5">
        <div class="w-2 h-2 bg-black rounded-full animate-bounce" />
        <div class="w-2 h-2 bg-black rounded-full animate-bounce [animation-delay:0.2s]" />
        <div class="w-2 h-2 bg-black rounded-full animate-bounce [animation-delay:0.4s]" />
      </div>
    {:else}
      <div class="prose dark:prose-invert max-w-none">
        {@html DOMPurify.sanitize(marked.parse(formattedMessage).toString())}
      </div>
    {/if}
  </div>
  <div bind:this={scrollToDiv} />
</div>
