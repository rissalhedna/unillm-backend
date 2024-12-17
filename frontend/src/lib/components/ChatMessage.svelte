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
  export { classes as class };

  let classes = "";
  let scrollToDiv: HTMLDivElement;

  const classSet = {
    user: "justify-end ",
    assistant: "justify-start ",
    system: "justify-center text-gray-400",
  };

  const classSetExtra = {
    user: "bg-gray-200",
    assistant: "",
    system: "j",
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

<div class="flex items-center {classSet[type]} ">
  <p class="px-2 text-xs">{type === "user" ? "Me" : "Bot"}</p>
</div>

<div class="flex {classSet[type]}">
  <div
    use:typeEffect={message}
    class="max-w-2xl rounded px-2 py-0.5 leading-loose {classes} {classSet[
      type
    ]} {classSetExtra[type]}"
  >
    {@html DOMPurify.sanitize(marked.parse(message))}
  </div>
  <div bind:this={scrollToDiv} />
</div>
