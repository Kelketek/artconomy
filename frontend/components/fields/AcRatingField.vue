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
                  :color="ratingColor[index as Ratings]"
                  :disabled="disabled"
                  v-if="index <= max"
                  variant="flat"
              >{{label}}</v-btn>
            </template>
          </v-btn-toggle>
        </v-col>
        <v-col cols="12" class="hidden-md-and-up">
          <v-row no-gutters>
            <v-col cols="12" v-for="(label, index) in ratingOptions" :key="label">
              <v-btn
                  :color="(String(scratch) === String(index)) ? ratingColor[index] : ''"
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
            <v-col class="text-center" cols="12"><h2>{{ratingOptions[scratch]}}</h2></v-col>
            <v-col class="text-center" cols="12">
              <span>
                {{ratingLongDesc[scratch]}}
              </span>
            </v-col>
            <v-col cols="12" v-if="showWarning && scratch === EXTREME">
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

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import {RATING_COLOR, RATING_LONG_DESC, RATINGS_SHORT} from '@/lib/lib.ts'
import ExtendedInput from '@/components/fields/mixins/extended_input.ts'
import {Ratings} from '@/types/Ratings.ts'

@Component({
  emits: ['update:modelValue'],
})
class AcRatingField extends mixins(ExtendedInput) {
  @Prop({default: false})
  public disabled!: boolean

  @Prop({required: true})
  public modelValue!: Ratings

  @Prop({default: 3})
  public max!: number

  @Prop({default: false})
  public showWarning!: boolean

  public ratingLabels = Object.values(RATINGS_SHORT)
  public ratingLongDesc = RATING_LONG_DESC
  public ratingColor = RATING_COLOR
  public ratingOptions = RATINGS_SHORT
  public EXTREME = 3

  public get scratch(): Ratings {
    return this.modelValue
  }

  public set scratch(val: Ratings) {
    this.$emit('update:modelValue', val)
  }
}

export default toNative(AcRatingField)
</script>
