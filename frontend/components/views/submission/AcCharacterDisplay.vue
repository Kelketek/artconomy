<template>
  <ac-load-section :controller="controller">
    <v-row dense>
      <v-tooltip
        v-if="editable"
        top
        aria-label="Tooltip for edit character button"
      >
        <template #activator="activator">
          <v-btn
            v-bind="activator.props"
            color="accent"
            icon
            size="small"
            class="mr-1"
            @click="toggle = true"
          >
            <v-icon :icon="mdiAccount" size="x-large" />
          </v-btn>
        </template>
        Edit Characters
      </v-tooltip>
      <v-tooltip v-else top aria-label="Tooltip for character listing">
        <template #activator="activator">
          <v-icon v-bind="activator.props" :icon="mdiAccountGroup" />
        </template>
        Characters
      </v-tooltip>
      <v-col v-if="controller.empty" align-self="center">
        No characters tagged.
      </v-col>
      <ac-mini-character
        v-for="item in controller.list"
        :key="item.x!.id"
        :character="item.x!.character"
        :alt="item.x!.character.name"
        class="mr-1"
      />
      <ac-expanded-property
        v-if="editable"
        v-model="toggle"
        aria-label="Character editing dialog"
      >
        <template #title> Characters </template>
        <ac-related-manager
          :field-controller="tagCharacter.fields.character_id"
          :list-controller="controller"
          item-key="character"
        >
          <template #preview="{ item }">
            <ac-mini-character
              :character="item.x.character"
              :removable="true"
              :alt="item.x.character.name"
              class="mr-1"
              @remove="item.delete().catch(tagCharacter.setErrors)"
            />
          </template>
          <template #default="{ filter }">
            <v-row class="mt-1">
              <v-col cols="12">
                <ac-bound-field
                  label="Tag Character"
                  hint="Enter the name of a character to tag them."
                  :field="tagCharacter.fields.character_id"
                  field-type="ac-character-select"
                  :multiple="false"
                  :autofocus="true"
                  :filter="filter"
                  :tagging="true"
                />
              </v-col>
            </v-row>
          </template>
        </ac-related-manager>
      </ac-expanded-property>
    </v-row>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from "../../wrappers/AcLoadSection.vue"
import AcRelatedManager from "../../wrappers/AcRelatedManager.vue"
import { ListController } from "@/store/lists/controller.ts"
import AcExpandedProperty from "@/components/wrappers/AcExpandedProperty.vue"
import AcBoundField from "@/components/fields/AcBoundField.ts"
import AcMiniCharacter from "@/components/AcMiniCharacter.vue"
import { mdiAccountGroup, mdiAccount } from "@mdi/js"
import { ref } from "vue"
import { useForm } from "@/store/forms/hooks.ts"
import type { LinkedCharacter } from "@/types/main"

const props = defineProps<{
  controller: ListController<LinkedCharacter>
  editable: boolean
}>()
const toggle = ref(false)
const tagCharacter = useForm(props.controller.name.value + "__tagCharacter", {
  fields: { character_id: { value: null } },
  endpoint: props.controller.endpoint,
})
</script>
