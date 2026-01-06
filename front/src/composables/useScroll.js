import { ref, watch, nextTick } from 'vue';

export function useScroll(containerRef) {
  const autoScroll = ref(true);

  const handleScroll = () => {
    if (!containerRef.value) return;

    const { scrollTop, scrollHeight, clientHeight } = containerRef.value;
    const distanceToBottom = scrollHeight - (scrollTop + clientHeight);

    autoScroll.value = distanceToBottom < 100;
  };

  const scrollToBottom = () => {
    if (containerRef.value) {
      containerRef.value.scrollTop = containerRef.value.scrollHeight;
    }
  };

  const watchMessages = (messages) => {
    watch(messages, () => {
      nextTick(() => {
        if (autoScroll.value && containerRef.value) {
          containerRef.value.scrollTop = containerRef.value.scrollHeight;
        }
      });
    }, { deep: true });
  };

  const initScrollListener = () => {
    watch(containerRef, (newVal) => {
      if (newVal) {
        newVal.addEventListener('scroll', handleScroll);
      }
    });
  };

  return {
    autoScroll,
    handleScroll,
    scrollToBottom,
    watchMessages,
    initScrollListener
  };
}
