<template>
  <v-col>
    <v-row no-gutters>
      <v-col
        class="text-center"
        cols="12"
      >
        Try terms like:
        <p>
          <v-chip
            color="secondary"
            variant="flat"
            class="mx-1"
            @click="search('fox')"
          >
            fox
          </v-chip>
          <v-chip
            color="secondary"
            variant="flat"
            class="mx-1"
            @click="search('wolf')"
          >
            wolf
          </v-chip>
          <v-chip
            color="secondary"
            variant="flat"
            class="mx-1"
            @click="search('male')"
          >
            male
          </v-chip>
          <v-chip
            color="secondary"
            variant="flat"
            class="mx-1"
            @click="search('female')"
          >
            female
          </v-chip>
        </p>
      </v-col>
    </v-row>
  </v-col>
</template>

<script setup lang="ts">
import {useForm} from '@/store/forms/hooks.ts'

const searchForm = useForm('search')
const search = (val: string) => searchForm.fields.q.model = val
</script>
