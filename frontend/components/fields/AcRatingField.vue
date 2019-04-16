<template>
  <v-input v-bind="passedProps" class="ac-rating-field">
    <v-card-text>
      <v-layout v-if="label" class="mb-5">
        <label :for="$attrs.id" class="v-label">{{label}}</label>
      </v-layout>
      <v-slider
          field-type="v-slider"
          v-model="scratch"
          :always-dirty="true"
          :max="max"
          step="1"
          ticks="always"
          tick-size="2"
          thumb-size="24"
          thumb-label="always"
          :color="ratingColor[scratch]"
          :disabled="disabled"
      >
        <template v-slot:thumb-label="props"></template>
      </v-slider>
      <v-layout row wrap :class="{disabled}">
        <v-flex xs12 text-xs-center><h2>{{ratingOptions[scratch]}}</h2></v-flex>
        <v-flex xs12 text-xs-center>
              <span v-text="ratingLongDesc[scratch]">
              </span>
        </v-flex>
      </v-layout>
    </v-card-text>
  </v-input>
</template>

<style scoped>
  .disabled {
    opacity: .5;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Component, {mixins} from 'vue-class-component'
import AcAsset from '../AcAsset.vue'
import {RATING_COLOR, RATING_LONG_DESC, RATINGS_SHORT} from '@/lib'
import {Prop} from 'vue-property-decorator'
import ExtendedInput from '@/components/fields/mixins/extended_input'

  @Component({
    components: {AcAsset},
  })
export default class AcRatingField extends mixins(ExtendedInput) {
    @Prop({default: false})
    public disabled!: boolean
    @Prop({required: true})
    public value!: number
    @Prop()
    public label!: string
    @Prop({default: 3})
    public max!: number
    public ratingLabels = Object.values(RATINGS_SHORT)
    public ratingLongDesc = RATING_LONG_DESC
    public ratingColor = RATING_COLOR
    public ratingOptions = RATINGS_SHORT

    public get scratch() {
      return this.value
    }
    public set scratch(val: number) {
      this.$emit('input', val)
    }
}
</script>