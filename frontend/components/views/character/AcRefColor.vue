<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
  <v-layout row wrap class="compact-fields">
    <v-flex xs12 sm7 md4 v-if="controls" v-show="editing">
      <ac-patch-field  :patcher="color.patchers.note"></ac-patch-field>
    </v-flex>
    <v-flex xs4 v-show="!editing">{{color.x.note}}</v-flex>
    <v-flex xs12 sm4 md2 offset-sm1 v-if="controls" v-show="editing">
      <ac-patch-field :patcher="color.patchers.color">
        <ac-color-prepend slot="prepend-inner" v-model="color.patchers.color.model"></ac-color-prepend>
      </ac-patch-field>
    </v-flex>
    <v-flex xs5 md4 text-xs-center color-notation v-show="!editing">{{color.x.color}}</v-flex>
    <v-flex xs10 md3 lg3 offset-md1 v-if="controls" v-show="editing">
      <v-flex px-2 :style="modelStyle">
        &nbsp;
      </v-flex>
    </v-flex>
    <v-flex xs2 md3 offset-xs1 v-show="!editing">
      <v-flex px-2 :style="savedStyle">&nbsp;</v-flex>
    </v-flex>
    <v-flex xs2 md1 text-xs-right text-lg-center v-if="editing">
      <ac-confirmation :action="color.delete">
        <span slot="confirmation-text">Are you sure you wish to delete this color? This cannot be undone.</span>
        <template v-slot:default="{on}">
          <v-btn small v-on="on" icon color="red" class="delete-button">
            <v-icon>delete</v-icon>
          </v-btn>
        </template>
      </ac-confirmation>
    </v-flex>
  </v-layout>
</template>

<style>
  .color-notation {
    font-family: monospace;
    text-transform: uppercase;
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Subjective from '@/mixins/subjective'
import {SingleController} from '@/store/singles/controller'
import Color from '@/store/characters/types/Color'
import {Prop} from 'vue-property-decorator'
import Editable from '@/mixins/editable'
import AcColorPrepend from '@/components/fields/AcColorPrepend.vue'

  @Component({
    components: {AcColorPrepend, AcPatchField, AcConfirmation},
  })
export default class AcRefColor extends mixins(Subjective, Editable) {
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
</script>
