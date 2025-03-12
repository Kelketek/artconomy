<template>
  <v-btn
    v-bind="attrs"
    class="rating-button"
    :variant="variant"
    :size="size"
    :color="RATING_COLOR[patcher.model]"
    :ripple="editing"
    @click="showRating"
  >
    <v-icon v-if="editing" left :icon="mdiPencil" />
    {{ RATINGS_SHORT[patcher.model] }}
  </v-btn>
  <ac-expanded-property
    v-if="controls"
    v-model="ratingDialog"
    aria-label="Edit rating dialog"
  >
    <ac-patch-field
      field-type="ac-rating-field"
      :patcher="patcher"
      class="rating-field"
    />
  </ac-expanded-property>
</template>

<script setup lang="ts">
import { ref, useAttrs } from "vue"
import AcExpandedProperty from "@/components/wrappers/AcExpandedProperty.vue"
import { mdiPencil } from "@mdi/js"
import { RATING_COLOR, RATINGS_SHORT } from "@/lib/lib.ts"
import { Patch } from "@/store/singles/patcher.ts"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import { RatingsValue } from "@/types/main"

const ratingDialog = ref(false)

const props = defineProps<{
  editing: boolean
  patcher: Patch<RatingsValue>
  controls: boolean
  variant?: "flat" | "text" | "elevated" | "tonal" | "outlined" | "plain"
  size?: string | number
}>()
const attrs = useAttrs()

const showRating = () => {
  if (props.editing && props.controls) {
    ratingDialog.value = true
  }
}

defineExpose({ ratingDialog })
</script>
