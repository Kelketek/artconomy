<template>
  <ac-load-section :controller="controller">
    <v-row dense>
      <v-tooltip top v-if="editable" aria-label="Tooltip for edit character button">
        <template v-slot:activator="{props}">
          <v-btn v-bind="props" @click="toggle=true" color="accent" icon size="small" class="mr-1">
            <v-icon :icon="mdiAccount" size="x-large"/>
          </v-btn>
        </template>
        Edit Characters
      </v-tooltip>
      <v-tooltip top v-else aria-label="Tooltip for character listing">
        <template v-slot:activator="{props}">
          <v-icon v-bind="props" :icon="mdiAccountGroup"/>
        </template>
        Characters
      </v-tooltip>
      <v-col align-self="center" v-if="controller.empty">
        No characters tagged.
      </v-col>
      <ac-mini-character :character="item.x!.character" v-for="item in controller.list" :key="item.x!.id" :alt="item.x!.character.name" class="mr-1"/>
      <ac-expanded-property v-model="toggle" v-if="editable" aria-label="Character editing dialog">
        <template v-slot:title>Characters</template>
        <ac-related-manager
            :field-controller="tagCharacter.fields.character_id" :list-controller="controller"
            item-key="character"
        >
          <template v-slot:preview="{item}">
              <ac-mini-character :character="item.x.character" :removable="true"
                                 :alt="item.x.character.name"
                                 @remove="item.delete().catch(tagCharacter.setErrors)" class="mr-1"/>
          </template>
          <template v-slot:default="{filter}">
            <v-row class="mt-1">
              <v-col cols="12">
                <ac-bound-field
                    label="Tag Character"
                    hint="Enter the name of a character to tag them."
                    :field="tagCharacter.fields.character_id" field-type="ac-character-select" :multiple="false"
                    :autofocus="true"
                    :filter="filter" :tagging="true"/>
              </v-col>
            </v-row>
          </template>
        </ac-related-manager>
      </ac-expanded-property>
    </v-row>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from '../../wrappers/AcLoadSection.vue'
import AcRelatedManager from '../../wrappers/AcRelatedManager.vue'
import {ListController} from '@/store/lists/controller.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcMiniCharacter from '@/components/AcMiniCharacter.vue'
import {mdiAccountGroup, mdiAccount} from '@mdi/js'
import {ref} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'
import type {LinkedCharacter} from '@/types/main'

const props = defineProps<{controller: ListController<LinkedCharacter>, editable: boolean}>()
const toggle = ref(false)
const tagCharacter = useForm(props.controller.name.value + '__tagCharacter', {
  fields: {character_id: {value: null}},
  endpoint: props.controller.endpoint,
})
</script>
