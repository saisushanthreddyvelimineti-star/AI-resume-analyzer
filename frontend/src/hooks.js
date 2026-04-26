import { useAnimation, useInView } from "framer-motion";
import { useEffect, useRef } from "react";

export function useMagnetic(strength = 0.28) {
  const ref = useRef(null);

  useEffect(() => {
    const node = ref.current;
    if (!node) return undefined;

    const handleMove = (event) => {
      const rect = node.getBoundingClientRect();
      const x = (event.clientX - rect.left - rect.width / 2) * strength;
      const y = (event.clientY - rect.top - rect.height / 2) * strength;
      node.style.transform = `translate(${x}px, ${y}px)`;
    };
    const handleLeave = () => {
      node.style.transform = "translate(0, 0)";
    };

    node.addEventListener("pointermove", handleMove);
    node.addEventListener("pointerleave", handleLeave);
    return () => {
      node.removeEventListener("pointermove", handleMove);
      node.removeEventListener("pointerleave", handleLeave);
    };
  }, [strength]);

  return ref;
}

export function useScrollReveal(options = { once: true, margin: "-80px" }) {
  const ref = useRef(null);
  const controls = useAnimation();
  const isInView = useInView(ref, options);

  useEffect(() => {
    if (isInView) controls.start("visible");
  }, [controls, isInView]);

  return { ref, controls };
}

