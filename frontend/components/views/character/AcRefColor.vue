<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
  <v-row no-gutters class="compact-fields" v-if="color.x">
    <v-col cols="12" sm="7" md="4" v-if="controls" v-show="editing">
      <ac-patch-field :patcher="color.patchers.note"/>
    </v-col>
    <v-col cols="4" v-show="!editing">{{color.x.note}}</v-col>
    <v-col cols="12" sm="4" md="2" offset-sm="1" v-if="controls" v-show="editing">
      <ac-patch-field :patcher="color.patchers.color">
        <template v-slot:prepend-inner>
          <ac-color-prepend v-model="color.patchers.color.model"/>
        </template>
      </ac-patch-field>
    </v-col>
    <v-col class="text-center color-notation" cols="5" md="4" v-show="!editing">{{color.x.color}}</v-col>
    <v-col cols="10" md="3" lg="3" offset-md="1" v-if="controls" v-show="editing" align-self="center">
      <v-col class="px-2" :style="modelStyle">
        &nbsp;
      </v-col>
    </v-col>
    <v-col cols="2" md="3" offset="1" v-show="!editing">
      <v-col class="px-2" :style="savedStyle">&nbsp;</v-col>
    </v-col>
    <v-col class="text-right text-lg-center" cols="2" md="1" v-if="editing">
      <ac-confirmation :action="color.delete">
        <template v-slot:confirmation-text>
          <span>Are you sure you wish to delete this color? This cannot be undone.</span>
        </template>
        <template v-slot:default="{on}">
          <v-btn size="x-small" icon v-on="on" color="red" class="delete-button">
            <v-icon icon="mdi-delete"/>
          </v-btn>
        </template>
      </ac-confirmation>
    </v-col>
  </v-row>
</template>

<style>
.color-notation {
  font-family: monospace;
  text-transform: uppercase;
}
</style>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Subjective from '@/mixins/subjective.ts'
import {SingleController} from '@/store/singles/controller.ts'
import Color from '@/store/characters/types/Color.ts'
import Editable from '@/mixins/editable.ts'
import AcColorPrepend from '@/components/fields/AcColorPrepend.vue'

@Component({
  components: {
    AcColorPrepend,
    AcPatchField,
    AcConfirmation,
  },
})
class AcRefColor extends mixins(Subjective, Editable) {
  public get modelStyle() {
    return {
      'background-color': this.color.patchers.color.model,
    }
  }

  public get savedStyle() {
    return {
      'background-color': this.color.patchers.color.rawValue,
    }
  }

  @Prop({required: true})
  public color!: SingleController<Color>
}

export default toNative(AcRefColor)
</script>
