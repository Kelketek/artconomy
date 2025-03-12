<template>
  <v-container fluid class="pa-0">
    <v-row class="d-flex">
      <v-col class="text-right">
        <v-btn
          v-if="controls"
          color="green"
          variant="flat"
          @click="showNew = true"
        >
          <v-icon left :icon="mdiPlus" />
          New Character
        </v-btn>
      </v-col>
    </v-row>
    <ac-paginated :list="characters">
      <v-col
        v-for="character in characters.list"
        :key="character.x!.id"
        class="pa-1"
        lg="2"
        md="3"
        cols="6"
      >
        <ac-character-preview
          :key="character.x!.id"
          :character="character.x!"
        />
      </v-col>
    </ac-paginated>
    <ac-form-dialog
      v-if="controls"
      v-model="showNew"
      v-bind="form.bind"
      title="New Character"
      @submit="form.submitThen(visitCharacter)"
    >
      <v-row no-gutters>
        <v-col cols="12">
          <ac-bound-field
            :field="form.fields.name"
            hint="Enter the name of your character."
            label="Character Name"
          />
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field
            :field="form.fields.private"
            field-type="ac-checkbox"
            :persistent-hint="true"
            label="Private"
            hint="If checked, this character will not appear in search listings and will only be visible to users you explicitly share them with."
          />
        </v-col>
        <v-col cols="12" sm="6">
          <ac-bound-field
            :field="form.fields.nsfw"
            field-type="ac-checkbox"
            :persistent-hint="true"
            label="NSFW"
            hint="If checked, this character will be hidden for users in SFW mode, or if they're
                          blocking a tag this character has in their NSFW blocked tags list. We recommend checking this
                          if you primarily draw/commission art of this character not appropriate for most workplace
                          settings."
          />
        </v-col>
      </v-row>
    </ac-form-dialog>
  </v-container>
</template>

<script setup lang="ts">
import AcCharacterPreview from "@/components/AcCharacterPreview.vue"
import AcPaginated from "@/components/wrappers/AcPaginated.vue"
import AcFormDialog from "@/components/wrappers/AcFormDialog.vue"
import AcBoundField from "@/components/fields/AcBoundField.ts"
import { flatten } from "@/lib/lib.ts"
import { mdiPlus } from "@mdi/js"
import { useList } from "@/store/lists/hooks.ts"
import { computed, ref } from "vue"
import { useForm } from "@/store/forms/hooks.ts"
import { useRouter } from "vue-router"
import { useSubject } from "@/mixins/subjective.ts"
import type { SubjectiveProps } from "@/types/main"
import { Character } from "@/store/characters/types/main"

const props = defineProps<SubjectiveProps>()
const { controls } = useSubject({ props })
const router = useRouter()
const showNew = ref(false)

const url = computed(() => {
  return `/api/profiles/account/${props.username}/characters/`
})

const characters = useList<Character>(`${flatten(props.username)}-characters`, {
  endpoint: url.value,
  keyProp: "name",
})

const form = useForm(`${flatten(props.username)}-newCharacter`, {
  endpoint: url.value,
  fields: {
    name: { value: "" },
    private: { value: false },
    nsfw: { value: false },
  },
})

characters.firstRun().then()

const visitCharacter = (character: Character) => {
  router.push({
    name: "Character",
    params: {
      username: props.username,
      characterName: character.name,
    },
    query: { editing: "true" },
  })
}
</script>
