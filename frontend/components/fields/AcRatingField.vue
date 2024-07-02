<template>
  <v-input v-bind="passedProps" class="ac-rating-field">
    <v-card-text>
      <v-row>
        <v-col cols="12" v-if="label">
          <label :for="$attrs.id as string || undefined" class="v-label">{{label}}</label>
        </v-col>
        <v-col cols="12" class="text-center hidden-sm-and-down">
          <v-btn-toggle v-model="scratch" mandatory elevation="3" variant="flat">
            <template v-for="(label, index) in ratingLabels">
              <v-btn
                  :value="index"
                  :key="label"
                  :color="RATING_COLOR[index as Ratings]"
                  :disabled="disabled"
                  v-if="index <= max"
                  variant="flat"
              >{{label}}</v-btn>
            </template>
          </v-btn-toggle>
        </v-col>
        <v-col cols="12" class="hidden-md-and-up">
          <v-row no-gutters>
            <v-col cols="12" v-for="(label, index) in RATINGS_SHORT" :key="label">
              <v-btn
                  :color="(String(scratch) === String(index)) ? RATING_COLOR[index] : ''"
                  @click="scratch = index"
                  :disabled="disabled"
                  block
                  variant="flat"
                  size="x-large"
                  v-if="index <= max"
              >{{label}}</v-btn>
            </v-col>
          </v-row>
        </v-col>
        <v-col cols="12" :class="{disabled}">
          <v-row>
            <v-col class="text-center" cols="12"><h2>{{RATINGS_SHORT[scratch]}}</h2></v-col>
            <v-col class="text-center" cols="12">
              <span>
                {{RATING_LONG_DESC[scratch]}}
              </span>
            </v-col>
            <v-col cols="12" v-if="showWarning && scratch === Ratings.EXTREME">
              <v-alert type="warning" class="my-2">
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

<style scoped>
.disabled {
  opacity: .5;
}
</style>

<script setup lang="ts">
import {RATING_COLOR, RATING_LONG_DESC, RATINGS_SHORT} from '@/lib/lib.ts'
import {ExtendedInputProps, useExtendedInput} from '@/components/fields/mixins/extended_input.ts'
import {Ratings} from '@/types/Ratings.ts'
import {computed} from 'vue'


const props = withDefaults(defineProps<{
  disabled?: boolean,
  modelValue: Ratings,
  max: number,
  showWarning: boolean,
} & ExtendedInputProps>(),{
  disabled: false,
  max: 3,
  showWarning: false,
})
const emit = defineEmits<{'update:modelValue': [Ratings]}>()

const scratch = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const {passedProps} = useExtendedInput(props)
const ratingLabels = Object.values(RATINGS_SHORT)
</script>
