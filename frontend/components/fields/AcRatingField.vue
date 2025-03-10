<template>
  <v-input
    v-bind="passedProps"
    class="ac-rating-field"
  >
    <v-card-text>
      <v-row>
        <v-col
          v-if="label"
          cols="12"
        >
          <label
            :for="attrs.id as string || undefined"
            class="v-label"
          >{{ label }}</label>
        </v-col>
        <v-col
          cols="12"
          class="text-center hidden-sm-and-down"
        >
          <v-btn-toggle
            v-model="scratch"
            mandatory
            elevation="3"
            variant="flat"
          >
            <template v-for="(label, index) in ratingLabels">
              <v-btn
                v-if="index <= max"
                :key="label"
                :value="index"
                :color="RATING_COLOR[index as RatingsValue]"
                :disabled="disabled"
                variant="flat"
              >
                {{ label }}
              </v-btn>
            </template>
          </v-btn-toggle>
        </v-col>
        <v-col
          cols="12"
          class="hidden-md-and-up"
        >
          <v-row no-gutters>
            <v-col
              v-for="(label, index) in RATINGS_SHORT"
              :key="label"
              cols="12"
            >
              <v-btn
                :color="(String(scratch) === String(index)) ? RATING_COLOR[index] : ''"
                v-if="index <= max"
                :disabled="disabled"
                block
                variant="flat"
                size="x-large"
                @click="scratch = index"
              >
                {{ label }}
              </v-btn>
            </v-col>
          </v-row>
        </v-col>
        <v-col
          cols="12"
          :class="{disabled}"
        >
          <v-row>
            <v-col
              class="text-center"
              cols="12"
            >
              <h2>{{ RATINGS_SHORT[scratch] }}</h2>
            </v-col>
            <v-col
              class="text-center"
              cols="12"
            >
              <span>
                {{ RATING_LONG_DESC[scratch] }}
              </span>
            </v-col>
            <v-col
              v-if="showWarning && scratch === Ratings.EXTREME"
              cols="12"
            >
              <v-alert
                type="warning"
                class="my-2"
              >
                What has been seen cannot be unseen. By selecting this rating you are willingly engaging with this
                content.
              </v-alert>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-card-text>
  </v-input>
</template>

<script setup lang="ts">
import {RATING_COLOR, RATING_LONG_DESC, RATINGS_SHORT} from '@/lib/lib.ts'
import {ExtendedInputProps, useExtendedInput} from '@/components/fields/mixins/extended_input.ts'
import {Ratings} from '@/types/enums/Ratings.ts'
import {computed, useAttrs} from 'vue'
import {RatingsValue} from '@/types/main'


const props = withDefaults(defineProps<{
  disabled?: boolean,
  modelValue: RatingsValue,
  max?: number,
  showWarning?: boolean,
} & ExtendedInputProps>(),{
  disabled: false,
  max: 3,
  showWarning: false,
})
const emit = defineEmits<{'update:modelValue': [RatingsValue]}>()

const scratch = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const {passedProps} = useExtendedInput(props)
const attrs = useAttrs()
const ratingLabels = Object.values(RATINGS_SHORT)
</script>

<style scoped>
.disabled {
  opacity: .5;
}
</style>
