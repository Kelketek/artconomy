<template>
  <ac-load-section :controller="colors" class="color-section">
    <v-row no-gutters class="mt-3" v-if="colors.list.length || editing">
      <v-col
          v-for="color in colors.list"
          :key="color.x!.id"
          :style="'background-color: ' + color.x!.color + ';' + 'height: 3rem;'"/>
    </v-row>
    <v-row no-gutters v-else/>
    <v-expansion-panels v-if="colors.list.length || editing">
      <v-expansion-panel>
        <v-expansion-panel-title>
          <v-row no-gutters>
            <v-col class="text-center">
              <v-icon left :icon="mdiPalette"/>
              Color References
            </v-col>
          </v-row>
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <template v-slot:default>
            <v-card-text>
              <template v-for="(color, index) in colors.list" :key="color.x!.id">
                <ac-ref-color :color="color" :username="username"/>
                <v-divider v-if="index + 1 < colors.list.length" :key="`color-${index}-divider`"/>
              </template>
              <ac-form @submit.prevent="newColor.submitThen(colors.push)" v-if="editing && colors.list.length < 24">
                <ac-form-container v-bind="newColor.bind">
                  <v-row>
                    <v-col><v-btn color="green" block @click="newColor.submitThen(postAdd)">Add Color</v-btn></v-col>
                  </v-row>
                </ac-form-container>
              </ac-form>
            </v-card-text>
          </template>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </ac-load-section>
</template>

<script setup lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {useSubject} from '@/mixins/subjective.ts'
import AcRefColor from '@/components/views/character/AcRefColor.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import {useCharacter} from '@/store/characters/hooks.ts'
import {useEditable} from '@/mixins/editable.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {mdiPalette} from '@mdi/js'
import type {CharacterProps} from '@/types/main'
import {Color} from '@/store/characters/types/main'

const props = defineProps<CharacterProps>()

const character = useCharacter(props)
const {controls} = useSubject({ props })
const colors = character.colors
const {editing} = useEditable(controls)

const exampleLines = [
  {note: 'Soul', color: '#000000'},
  {note: 'Beans', color: '#fa6982'},
  {note: 'Friendship Bracelet', color: '#50c336'},
  {note: 'Blood', color: '#151aaa'},
  {note: 'Boogers', color: '#74a82a'},
  {note: 'Skin Tone', color: '#631262'},
  {note: 'Phone Case', color: '#f59b14'},
  {note: 'Shoes', color: '#e9f514'},
  {note: 'Hat', color: '#14f5ed'}
]

const randomColor = () => exampleLines[Math.floor(Math.random() * exampleLines.length)]

const exampleLine = randomColor()

const newColor = useForm(`${character.colors.name.value}__newColor`, {
  endpoint: colors.endpoint,
  fields: {
    note: {
      value: exampleLine.note,
    },
    color: {
      value: exampleLine.color,
    },
  },
})

const postAdd = (color: Color) => {
  colors.push(color)
  const exampleLine = randomColor()
  newColor.fields.note.update(exampleLine.note)
  newColor.fields.color.update(exampleLine.color)
}

colors.firstRun()
</script>
