<template>
  <ac-load-section :controller="character.colors" class="color-section">
    <v-layout row class="mt-3" v-if="character.colors.list.length || editing">
      <v-flex
          v-for="color in character.colors.list"
          :key="color.x.id"
          :style="'background-color: ' + color.x.color + ';' + 'height: 3rem;'"/>
    </v-layout>
    <v-layout v-else></v-layout>
    <v-expansion-panel v-if="character.colors.list.length || editing">
      <v-expansion-panel-content>
        <v-flex slot="header" class="text-xs-center">
          <v-icon left>palette</v-icon> Color References
        </v-flex>
        <v-card-text>
          <template v-for="(color, index) in character.colors.list">
            <ac-ref-color :color="color" :key="color.id" :username="username"></ac-ref-color>
            <v-divider v-if="index + 1 < character.colors.list.length" :key="`color-${index}-divider`"></v-divider>
          </template>
            <form @submit.prevent="newColor.submitThen(character.colors.push)" v-if="editing && character.colors.list.length < 10" :id="newColor.bind.id">
              <ac-form-container>
                <v-layout row wrap class="compact-fields">
                  <v-flex xs12><v-divider></v-divider></v-flex>
                  <v-flex xs12 sm7 md4>
                    <ac-bound-field :field="newColor.fields.note"
                                    label="Note"
                                    hint="Label this color so others know what it's for. 'Hair', 'Eyes', or 'Hat' are all examples.">
                    </ac-bound-field>
                  </v-flex>
                  <v-flex xs12 sm4 md2 offset-sm1>
                    <ac-bound-field :field="newColor.fields.color">
                      <ac-color-prepend slot="prepend-inner" v-model="newColor.fields.color.model"></ac-color-prepend>
                    </ac-bound-field>
                  </v-flex>
                  <v-flex xs10 md3 lg3 offset-md1>
                    <v-flex px-2 :style="newColorStyle">&nbsp;</v-flex>
                  </v-flex>
                  <v-flex xs2 md1 text-xs-right text-lg-center>
                    <v-btn icon color="black" type="submit">
                      <v-icon color="yellow">save</v-icon>
                    </v-btn>
                  </v-flex>
                </v-layout>
              </ac-form-container>
            </form>
        </v-card-text>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </ac-load-section>
</template>

<style scoped>
  .ref-container {
    opacity: 0;
    padding: .1rem;
    display: inline-block;
  }

  .swatch {
    width: 100%;
    border: 2px solid #e0e0e0;
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Subjective from '@/mixins/subjective'
import CharacterCentric from '@/components/views/character/mixins/CharacterCentric'
import Editable from '@/mixins/editable'
import Color from '@/store/characters/types/Color'
import {ListController} from '@/store/lists/controller'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcRefColor from '@/components/views/character/AcRefColor.vue'
import {FormController} from '@/store/forms/form-controller'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import {flatten} from '@/lib'
import {Watch} from 'vue-property-decorator'
import AcColorPrepend from '@/components/fields/AcColorPrepend.vue'

  @Component({
    components: {AcColorPrepend, AcBoundField, AcFormContainer, AcRefColor, AcPatchField, AcConfirmation, AcLoadSection},
  })
export default class AcColors extends mixins(Subjective, CharacterCentric, Editable) {
    public colors: ListController<Color> = null as unknown as ListController<Color>
    public newColor: FormController = null as unknown as FormController

    @Watch('character.colors.endpoint')
    public updateEndpoint(value: string|undefined) {
      // If this is true, we're tearing down and should ignore.
      /* istanbul ignore if */
      if (value === undefined) {
        return
      }
      this.newColor.endpoint = value
    }

    public get newColorStyle() {
      return {
        'background-color': this.newColor.fields.color.value,
      }
    }

    public created() {
      this.newColor = this.$getForm(flatten(`${flatten(this.character.colors.name)}/newColor`), {
        endpoint: this.character.colors.endpoint,
        fields: {
          note: {value: '', validators: [{name: 'required'}]},
          color: {value: '#000000', validators: [{name: 'required'}, {name: 'colorRef'}]},
        },
      })
      this.character.colors.firstRun().then()
    }
}
</script>
