<template>
  <ac-load-section :controller="character.attributes">
    <template #error-text>
      We had an issue while trying to load {{ characterName }}'s attributes.
    </template>
    <v-container class="pa-0 compact-fields">
      <v-row v-if="controls" v-show="editing" no-gutters>
        <v-col
          v-for="attribute in character.attributes.list"
          :key="attribute.x!.id"
          cols="12"
        >
          <v-row no-gutters>
            <v-col v-if="attribute.x!.sticky" cols="5" class="attr-input">
              <ac-patch-field
                :disabled="true"
                :value="attribute.x!.key"
                :save-indicator="false"
                density="compact"
                :patcher="attribute.patchers.key"
              />
            </v-col>
            <v-col v-else class="d-flex attr-input" cols="5">
              <ac-patch-field
                disabled
                :patcher="attribute.patchers.key"
                density="compact"
              />
            </v-col>
            <v-col class="d-flex" cols="5" lg="6">
              <ac-patch-field
                :patcher="attribute.patchers.value"
                density="compact"
              />
            </v-col>
            <v-col v-if="!attribute.x!.sticky" class="d-flex" cols="2" lg="1">
              <v-row no-gutters class="text-center">
                <ac-confirmation :action="attribute.delete">
                  <template #default="{ on }">
                    <v-btn
                      color="red"
                      icon
                      variant="plain"
                      size="small"
                      type="submit"
                      v-on="on"
                    >
                      <v-icon :icon="mdiDelete" />
                    </v-btn>
                  </template>
                </ac-confirmation>
              </v-row>
            </v-col>
          </v-row>
        </v-col>
      </v-row>
      <ac-form
        v-if="character.attributes.list.length < 10"
        @submit.prevent="newAttribute.submitThen(addAttribute)"
      >
        <ac-form-container
          v-if="controls"
          v-show="editing"
          :sending="newAttribute.sending"
          :errors="newAttribute.errors"
        >
          <v-row no-gutters>
            <v-col class="attr-input" cols="5">
              <ac-bound-field
                ref="attrKey"
                :field="newAttribute.fields.key"
                label="Attribute"
                density="compact"
              />
            </v-col>
            <v-col cols="5" lg="6">
              <ac-bound-field
                :field="newAttribute.fields.value"
                label="Value"
                density="compact"
              />
            </v-col>
            <v-col cols="2" lg="1" class="d-flex">
              <v-col class="text-center">
                <v-btn
                  color="black"
                  icon
                  elevation="0"
                  type="submit"
                  size="x-small"
                  class="submit-attribute"
                >
                  <v-icon color="yellow" :icon="mdiContentSave" />
                </v-btn>
              </v-col>
            </v-col>
          </v-row>
        </ac-form-container>
      </ac-form>
      <v-col
        v-for="(attribute, index) in character.attributes.list"
        v-show="!editing"
        :key="attribute.x!.id"
      >
        <v-row no-gutters>
          <v-col class="attr-key" cols="3">
            {{ attribute.x!.key }}
          </v-col>
          <v-col cols="9">
            {{ attribute.x!.value }}
          </v-col>
          <v-col
            v-if="index + 1 !== character.attributes.list.length"
            cols="12"
          >
            <v-divider />
          </v-col>
        </v-row>
      </v-col>
    </v-container>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from "@/components/wrappers/AcLoadSection.vue"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import AcConfirmation from "@/components/wrappers/AcConfirmation.vue"
import AcFormContainer from "@/components/wrappers/AcFormContainer.vue"
import AcBoundField from "@/components/fields/AcBoundField.ts"
import { useSubject } from "@/mixins/subjective.ts"
import { artCall } from "@/lib/lib.ts"
import AcForm from "@/components/wrappers/AcForm.vue"
import { mdiContentSave, mdiDelete } from "@mdi/js"
import { useCharacter } from "@/store/characters/hooks.ts"
import { computed, nextTick, ref, watch } from "vue"
import { useForm } from "@/store/forms/hooks.ts"
import { useEditable } from "@/mixins/editable.ts"
import type { Attribute, CharacterProps } from "@/types/main"
import { Character } from "@/store/characters/types/main"

const props = defineProps<CharacterProps>()
const { controls } = useSubject({ props })
const { editing } = useEditable(controls)
const character = useCharacter(props)

const cancelSource = ref(new AbortController())

const newAttribute = useForm(
  `${character.attributes.name.value}__newAttribute`,
  {
    endpoint: character.attributes.endpoint,
    fields: {
      key: { value: "" },
      value: { value: "" },
    },
  },
)
character.attributes.firstRun().then()

const stickies = computed(() => {
  const stickied: string[] = []
  character.attributes.list.forEach((attribute) => {
    if (attribute.x && attribute.x.sticky) {
      stickied.push(attribute.x.value)
    }
  })
  return new Set(stickied)
})

const addAttribute = (result: Attribute) => {
  character.attributes.push(result)
  const element = document.querySelector(
    "#" + newAttribute.fields.key.id,
  ) as HTMLInputElement
  /* istanbul ignore if */
  if (!element) {
    return
  }
  element.focus()
  nextTick(() => {
    newAttribute.stopValidators()
    nextTick(() => {
      newAttribute.clearErrors()
    })
  })
}

watch(
  () => character.attributes.endpoint,
  (value) => {
    newAttribute.endpoint = value
  },
)

watch(stickies, (newVal: Set<string>, oldVal?: Set<string>) => {
  if (oldVal === undefined) {
    return
  }
  // Does this work for sets?
  if (newVal === oldVal) {
    return
  }
  cancelSource.value.abort()
  cancelSource.value = new AbortController()
  artCall({
    url: character.profile.endpoint,
    method: "get",
    signal: cancelSource.value.signal,
  }).then((characterData: Character) => {
    character.profile.updateX({ tags: characterData.tags })
  })
})
</script>

<style>
.attr-key,
.attr-input .v-text-field__slot input {
  font-weight: bold;
  text-transform: uppercase;
}

.compact-fields .v-label--active {
  top: 13px;
  font-size: 12px;
}
</style>
