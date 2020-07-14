<template xmlns:v-slot="http://www.w3.org/1999/XSL/Transform">
  <v-row no-gutters   class="compact-fields">
    <v-col cols="12" sm="7" md="4" v-if="controls" v-show="editing">
      <ac-patch-field  :patcher="color.patchers.note" />
    </v-col>
    <v-col cols="4" v-show="!editing">{{color.x.note}}</v-col>
    <v-col cols="12" sm="4" md="2" offset-sm="1" v-if="controls" v-show="editing">
      <ac-patch-field :patcher="color.patchers.color">
        <ac-color-prepend slot="prepend-inner" v-model="color.patchers.color.model" />
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
        <span slot="confirmation-text">Are you sure you wish to delete this color? This cannot be undone.</span>
        <template v-slot:default="{on}">
          <v-btn x-small fab v-on="on" color="red" class="delete-button">
            <v-icon>delete</v-icon>
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
