<template>
  <v-btn v-bind="attrs" class="rating-button" :variant="variant" :size="size" :color="RATING_COLOR[patcher.model]"
         @click="showRating" :ripple="editing">
    <v-icon left v-if="editing" :icon="mdiPencil"/>
    {{RATINGS_SHORT[patcher.model]}}
  </v-btn>
  <ac-expanded-property v-model="ratingDialog" aria-label="Edit rating dialog" v-if="controls">
    <ac-patch-field field-type="ac-rating-field" :patcher="patcher" class="rating-field"/>
  </ac-expanded-property>
</template>

<script setup lang="ts">
import {ref, useAttrs} from 'vue'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import {mdiPencil} from '@mdi/js'
import {RATING_COLOR, RATINGS_SHORT} from '@/lib/lib.ts'
import {ContentRating} from '@/types/ContentRating.ts'
import {Patch} from '@/store/singles/patcher.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'

const ratingDialog = ref(false)

const props = defineProps<{
  editing: boolean,
  patcher: Patch<ContentRating>,
  controls: boolean,
  variant?: "flat" | "text" | "elevated" | "tonal" | "outlined" | "plain",
  size?: string|number,
}>()
const attrs = useAttrs()

const showRating = () => {
  if (props.editing && props.controls) {
    ratingDialog.value = true
  }
}

defineExpose({ratingDialog})
</script>
