<template>
  <ac-load-section :controller="character.colors" class="color-section">
    <v-row no-gutters class="mt-3" v-if="character.colors.list.length || editing">
      <v-col
          v-for="color in character.colors.list"
          :key="color.x.id"
          :style="'background-color: ' + color.x.color + ';' + 'height: 3rem;'"/>
    </v-row>
    <v-row no-gutters v-else />
    <v-expansion-panels v-if="character.colors.list.length || editing">
      <v-expansion-panel>
        <v-expansion-panel-header>
          <v-col class="text-center">
            <v-icon left>palette</v-icon> Color References
          </v-col>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <v-card-text>
            <template v-for="(color, index) in character.colors.list">
              <ac-ref-color :color="color" :key="color.id" :username="username" />
              <v-divider v-if="index + 1 < character.colors.list.length" :key="`color-${index}-divider`" />
            </template>
            <ac-form @submit.prevent="newColor.submitThen(character.colors.push)" v-if="editing && character.colors.list.length < 10" :id="newColor.bind.id">
              <ac-form-container>
                <v-row no-gutters  class="compact-fields">
                  <v-col cols="12"><v-divider></v-divider></v-col>
                  <v-col cols="12" sm="7" md="4">
                    <ac-bound-field :field="newColor.fields.note"
                                    label="Note"
                                    hint="Label this color so others know what it's for. 'Hair', 'Eyes', or 'Hat' are all examples.">
                    </ac-bound-field>
                  </v-col>
                  <v-col cols="12" sm="4" md="2" offset-sm="1">
                    <ac-bound-field :field="newColor.fields.color">
                      <ac-color-prepend slot="prepend-inner" v-model="newColor.fields.color.model" />
                    </ac-bound-field>
                  </v-col>
                  <v-col cols="10" md="3" lg="3" offset-md="1" align-self="center">
                    <v-col class="px-2" :style="newColorStyle">&nbsp;</v-col>
                  </v-col>
                  <v-col class="text-right text-lg-center" cols="2" md="1" >
                    <v-btn x-small fab color="black" type="submit">
                      <v-icon color="yellow">save</v-icon>
                    </v-btn>
                  </v-col>
                </v-row>
              </ac-form-container>
            </ac-form>
          </v-card-text>
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
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
import {flatten} from '@/lib/lib'
import {Watch} from 'vue-property-decorator'
import AcColorPrepend from '@/components/fields/AcColorPrepend.vue'
import AcForm from '@/components/wrappers/AcForm.vue'

@Component({
  components: {
    AcForm,
    AcColorPrepend,
    AcBoundField,
    AcFormContainer,
    AcRefColor,
    AcPatchField,
    AcConfirmation,
    AcLoadSection,
  },
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
