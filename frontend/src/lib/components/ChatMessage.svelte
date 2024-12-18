<script lang="ts">
  import { marked } from "marked";
  import DOMPurify from "isomorphic-dompurify";
  import { onMount } from "svelte";

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
      <div class="prose prose-slate dark:prose-invert max-w-none prose-pre:bg-gray-100 dark:prose-pre:bg-gray-800 prose-pre:p-2 prose-pre:rounded-lg prose-code:text-pink-500 dark:prose-code:text-pink-400 prose-headings:mb-2 prose-p:mb-2 prose-ul:my-2 prose-li:my-0">
        {@html DOMPurify.sanitize(marked.parse(message).toString())}
      </div>
    {/if}
  </div>
  <div bind:this={scrollToDiv} />
</div>
