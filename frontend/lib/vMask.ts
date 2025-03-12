import {
  makeDirective,
  masker,
  filterNumbers,
  // @ts-expect-error Types not worth shimming.
} from "@devindex/vue-mask/dist/vue-mask.esm.js"

export const vMaskToken = makeDirective(
  masker(() => ({
    pattern: "000 000",
    pre: filterNumbers,
  })),
)
