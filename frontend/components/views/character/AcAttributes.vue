<template>
  <ac-load-section :controller="character.attributes">
    <template v-slot:error-text>We had an issue while trying to load {{characterName}}'s attributes.</template>
    <v-container class="pa-0 compact-fields">
      <v-row v-if="controls" v-show="editing" no-gutters>
        <v-col v-for="attribute in character.attributes.list" :key="attribute.x!.id" cols="12">
          <v-row no-gutters>
            <v-col cols="5" class="attr-input" v-if="attribute.x!.sticky">
              <ac-patch-field
                  :disabled="true" :value="attribute.x!.key"
                  :save-indicator="false"
                  density="compact"
                  :patcher="attribute.patchers.key"/>
            </v-col>
            <v-col class="d-flex attr-input" cols="5" v-else>
              <ac-patch-field disabled :patcher="attribute.patchers.key" density="compact" />
            </v-col>
            <v-col class="d-flex" cols="5" lg="6">
              <ac-patch-field :patcher="attribute.patchers.value" density="compact" />
            </v-col>
            <v-col class="d-flex" cols="2" lg="1" v-if="!attribute.x!.sticky">
              <v-row no-gutters class="text-center">
                <ac-confirmation :action="attribute.delete">
                  <template v-slot:default="{on}">
                    <v-btn color="red" icon small type="submit" v-on="on">
                      <v-icon icon="mdi-delete"/>
                    </v-btn>
                  </template>
                </ac-confirmation>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <ac-form @submit.prevent="newAttribute.submitThen(addAttribute)" v-if="character.attributes.list.length < 10">
        <ac-form-container v-if="controls" v-show="editing" :sending="newAttribute.sending"
                           :errors="newAttribute.errors">
          <v-row no-gutters>
            <v-col class="attr-input" cols="5">
              <ac-bound-field ref="attrKey" :field="newAttribute.fields.key" label="Attribute" density="compact" />
            </v-col>
            <v-col cols="5" lg="6">
              <ac-bound-field :field="newAttribute.fields.value" label="Value" density="compact" />
            </v-col>
            <v-col cols="2" lg="1" class="d-flex">
              <v-col class="text-center">
                <v-btn color="black" icon elevation="0" type="submit" size="x-small" class="submit-attribute">
                  <v-icon color="yellow" icon="mdi-content-save"/>
                </v-btn>
              </v-col>
            </v-col>
          </v-row>
        </ac-form-container>
      </ac-form>
      <v-col v-for="(attribute, index) in character.attributes.list" :key="attribute.x!.id" v-show="!editing">
        <v-row no-gutters>
          <v-col class="attr-key" cols="3">{{attribute.x!.key}}</v-col>
          <v-col cols="9">{{attribute.x!.value}}</v-col>
          <v-col cols="12" v-if="index + 1 !== character.attributes.list.length">
            <v-divider/>
          </v-col>
        </v-row>
      </v-col>
    </v-container>
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
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
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
import {artCall} from '@/lib/lib'
import axios from 'axios'
import {Character} from '@/store/characters/types/Character'
import AcForm from '@/components/wrappers/AcForm.vue'

@Component({
  components: {
    AcForm,
    AcBoundField,
    AcFormContainer,
    AcConfirmation,
    AcPatchField,
    AcLoadSection,
  },
})
class AcAttributes extends mixins(Subjective, CharacterCentric, Editable) {
  public newAttribute: FormController = null as unknown as FormController
  public cancelSource = new AbortController()

  @Watch('stickies')
  public updateTags(newVal: string[], oldVal: string[]) {
    if (oldVal === null) {
      return
    }
    if (this.character && deepEqual(newVal, oldVal)) {
      return
    }
    this.cancelSource.abort()
    this.cancelSource = new AbortController()
    artCall({
      url: this.character.profile.endpoint,
      method: 'get',
      signal: this.cancelSource.signal,
    }).then(
        (character: Character) => {
          this.character.profile.updateX({tags: character.tags})
        })
  }

  @Watch('character.attributes.endpoint')
  public updateEndpoint(value: string | undefined) {
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
    return this.character.attributes.list.filter((attribute) => {
      if (attribute.x && attribute.x.sticky) {
        return attribute.x.value
      }
      return undefined
    })
  }

  public created() {
    this.newAttribute = this.$getForm(`${this.character.attributes.name}__newAttribute`, {
      endpoint: this.character.attributes.endpoint,
      fields: {
        key: {value: ''},
        value: {value: ''},
      },
    })
    this.character.attributes.firstRun().then()
  }
}

export default toNative(AcAttributes)
</script>
