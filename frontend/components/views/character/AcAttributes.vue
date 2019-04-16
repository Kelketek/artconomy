<template>
  <ac-load-section :controller="character.attributes">
    <span slot="error-text">We had an issue while trying to load {{characterName}}'s attrbutes.</span>
    <v-layout column class="compact-fields">
      <v-flex v-if="controls" v-show="editing">
        <v-flex v-for="attribute in character.attributes.list" :key="attribute.id">
          <v-layout row wrap>
            <v-flex d-flex xs5 attr-input v-if="attribute.x.sticky">
              <ac-patch-field
                  :disabled="true" :value="attribute.x.key"
                  :save-indicator="false"
                  :patcher="attribute.patchers.key"></ac-patch-field>
            </v-flex>
            <v-flex d-flex xs5 attr-input v-else>
              <ac-patch-field disabled :patcher="attribute.patchers.key"></ac-patch-field>
            </v-flex>
            <v-flex d-flex xs5 lg6>
              <ac-patch-field :patcher="attribute.patchers.value"></ac-patch-field>
            </v-flex>
            <v-flex class xs2 lg1 column d-flex v-if="!attribute.x.sticky">
              <v-flex text-xs-center>
                <ac-confirmation v :action="attribute.delete">
                  <template v-slot:default="{on}">
                    <v-btn color="red" icon small type="submit" v-on="on">
                      <v-icon>delete</v-icon>
                    </v-btn>
                  </template>
                </ac-confirmation>
              </v-flex>
            </v-flex>
          </v-layout>
        </v-flex>
      </v-flex>
      <form @submit.prevent="newAttribute.submitThen(addAttribute)" v-if="character.attributes.list.length < 10">
        <ac-form-container v-if="controls" v-show="editing" :sending="newAttribute.sending" :errors="newAttribute.errors">
          <v-layout row wrap>
            <v-flex xs5 attr-input>
              <ac-bound-field ref="attrKey" :field="newAttribute.fields.key" label="Attribute"></ac-bound-field>
            </v-flex>
            <v-flex xs5 lg6>
              <ac-bound-field :field="newAttribute.fields.value" label="Value"></ac-bound-field>
            </v-flex>
            <v-flex xs2 lg1 column d-flex>
              <v-flex text-xs-center>
                <v-btn color="black" icon type="submit" small class="submit-attribute">
                  <v-icon color="yellow">save</v-icon>
                </v-btn>
              </v-flex>
            </v-flex>
          </v-layout>
        </ac-form-container>
      </form>
      <v-flex v-for="(attribute, index) in character.attributes.list" :key="attribute.id" v-show="!editing">
        <v-layout row wrap>
          <v-flex xs3 attr-key>{{attribute.x.key}}</v-flex>
          <v-flex xs9>{{attribute.x.value}}</v-flex>
          <v-flex xs12 v-if="index + 1 !== character.attributes.list.length"><v-divider></v-divider></v-flex>
        </v-layout>
      </v-flex>
    </v-layout>
  </ac-load-section>
</template>

<style>
  .attr-key, .attr-input .v-text-field__slot input {
    font-weight: bold;
    text-transform: uppercase;
  }
  .compact-fields .v-label--active {
    top: 13px;
    font-size: 12px;
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import deepEqual from 'fast-deep-equal'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import Subjective from '@/mixins/subjective'
import Attribute from '@/types/Attribute'
import {FormController} from '@/store/forms/form-controller'
import CharacterCentric from '@/components/views/character/mixins/CharacterCentric'
import Editable from '@/mixins/editable'
import {artCall, flatten} from '@/lib'
import {Watch} from 'vue-property-decorator'
import axios from 'axios'
import {Character} from '@/store/characters/types/Character'

  @Component({
    components: {AcBoundField, AcFormContainer, AcConfirmation, AcPatchField, AcLoadSection},
  })
export default class AcAttributes extends mixins(Subjective, CharacterCentric, Editable) {
    public newAttribute: FormController = null as unknown as FormController
    public cancelSource = axios.CancelToken.source()

    @Watch('stickies')
    public updateTags(newVal: string[], oldVal: string[]) {
      if (oldVal === null) {
        return
      }
      if (this.character && deepEqual(newVal, oldVal)) {
        return
      }
      this.cancelSource.cancel()
      this.cancelSource = axios.CancelToken.source()
      artCall({url: this.character.profile.endpoint, method: 'get', cancelToken: this.cancelSource.token}).then(
        (character: Character) => {
          this.character.profile.updateX({tags: character.tags})
        })
    }
    @Watch('character.attributes.endpoint')
    public updateEndpoint(value: string|undefined) {
      /* istanbul ignore if */
      if (value === undefined) {
        return
      }
      this.newAttribute.endpoint = value
    }
    public addAttribute(result: Attribute) {
      this.character.attributes.push(result)
      const element = document.querySelector('#' + this.newAttribute.fields.key.id) as HTMLInputElement
      /* istanbul ignore if */
      if (!element) {
        return
      }
      element.focus()
      this.$nextTick(() => {
        this.newAttribute.stopValidators()
        this.$nextTick(() => {
          this.newAttribute.clearErrors()
        })
      })
    }
    public get stickies() {
      if (!this.character) {
        return null
      }
      return this.character.attributes.list.map((attribute) => {
        if (attribute.x && attribute.x.sticky) {
          return attribute.x.value
        }
      })
    }
    public created() {
      this.newAttribute = this.$getForm(flatten(`${this.character.attributes.name}/newAttribute`), {
        endpoint: this.character.attributes.endpoint,
        fields: {
          key: {value: '', validators: [{name: 'required'}]},
          value: {value: '', validators: [{name: 'required'}]},
        },
      })
      this.character.attributes.firstRun().then()
    }
}
</script>
